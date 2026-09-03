"""Carga segura e idempotente del catálogo ISO 3166-1 usado por SGPC.

El comando crea los países que falten y completa códigos ISO en registros
existentes sin borrar filas ni cambiar claves primarias. Por defecto funciona
en modo vista previa. Para aplicar cambios exige --aplicar y confirmación.
Con ``--actualizar-nombres`` puede normalizar etiquetas al español.
"""

import re
import unicodedata

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Pais


# ISO 3166-1 vigente. Los nombres en español son etiquetas de presentación;
# iso2/iso3 son las claves estables utilizadas para reconciliar el catálogo.
# El cuarto valor permite reconocer catálogos antiguos cargados en inglés.
PAISES_ISO = (
    ('AD', 'AND', 'Andorra', 'Andorra'),
    ('AE', 'ARE', 'Emiratos Árabes Unidos', 'United Arab Emirates'),
    ('AF', 'AFG', 'Afganistán', 'Afghanistan'),
    ('AG', 'ATG', 'Antigua y Barbuda', 'Antigua and Barbuda'),
    ('AI', 'AIA', 'Anguila', 'Anguilla'),
    ('AL', 'ALB', 'Albania', 'Albania'),
    ('AM', 'ARM', 'Armenia', 'Armenia'),
    ('AO', 'AGO', 'Angola', 'Angola'),
    ('AQ', 'ATA', 'Antártida', 'Antarctica'),
    ('AR', 'ARG', 'Argentina', 'Argentina'),
    ('AS', 'ASM', 'Samoa Americana', 'American Samoa'),
    ('AT', 'AUT', 'Austria', 'Austria'),
    ('AU', 'AUS', 'Australia', 'Australia'),
    ('AW', 'ABW', 'Aruba', 'Aruba'),
    ('AX', 'ALA', 'Islas Åland', 'Åland Islands'),
    ('AZ', 'AZE', 'Azerbaiyán', 'Azerbaijan'),
    ('BA', 'BIH', 'Bosnia y Herzegovina', 'Bosnia and Herzegovina'),
    ('BB', 'BRB', 'Barbados', 'Barbados'),
    ('BD', 'BGD', 'Bangladés', 'Bangladesh'),
    ('BE', 'BEL', 'Bélgica', 'Belgium'),
    ('BF', 'BFA', 'Burkina Faso', 'Burkina Faso'),
    ('BG', 'BGR', 'Bulgaria', 'Bulgaria'),
    ('BH', 'BHR', 'Baréin', 'Bahrain'),
    ('BI', 'BDI', 'Burundi', 'Burundi'),
    ('BJ', 'BEN', 'Benín', 'Benin'),
    ('BL', 'BLM', 'San Bartolomé', 'Saint Barthélemy'),
    ('BM', 'BMU', 'Bermudas', 'Bermuda'),
    ('BN', 'BRN', 'Brunéi', 'Brunei Darussalam'),
    ('BO', 'BOL', 'Bolivia', 'Bolivia, Plurinational State of'),
    ('BQ', 'BES', 'Caribe neerlandés', 'Bonaire, Sint Eustatius and Saba'),
    ('BR', 'BRA', 'Brasil', 'Brazil'),
    ('BS', 'BHS', 'Bahamas', 'Bahamas'),
    ('BT', 'BTN', 'Bután', 'Bhutan'),
    ('BV', 'BVT', 'Isla Bouvet', 'Bouvet Island'),
    ('BW', 'BWA', 'Botsuana', 'Botswana'),
    ('BY', 'BLR', 'Bielorrusia', 'Belarus'),
    ('BZ', 'BLZ', 'Belice', 'Belize'),
    ('CA', 'CAN', 'Canadá', 'Canada'),
    ('CC', 'CCK', 'Islas Cocos', 'Cocos (Keeling) Islands'),
    ('CD', 'COD', 'República Democrática del Congo', 'Congo, The Democratic Republic of the'),
    ('CF', 'CAF', 'República Centroafricana', 'Central African Republic'),
    ('CG', 'COG', 'Congo', 'Congo'),
    ('CH', 'CHE', 'Suiza', 'Switzerland'),
    ('CI', 'CIV', 'Costa de Marfil', "Côte d'Ivoire"),
    ('CK', 'COK', 'Islas Cook', 'Cook Islands'),
    ('CL', 'CHL', 'Chile', 'Chile'),
    ('CM', 'CMR', 'Camerún', 'Cameroon'),
    ('CN', 'CHN', 'China', 'China'),
    ('CO', 'COL', 'Colombia', 'Colombia'),
    ('CR', 'CRI', 'Costa Rica', 'Costa Rica'),
    ('CU', 'CUB', 'Cuba', 'Cuba'),
    ('CV', 'CPV', 'Cabo Verde', 'Cabo Verde'),
    ('CW', 'CUW', 'Curazao', 'Curaçao'),
    ('CX', 'CXR', 'Isla de Navidad', 'Christmas Island'),
    ('CY', 'CYP', 'Chipre', 'Cyprus'),
    ('CZ', 'CZE', 'Chequia', 'Czechia'),
    ('DE', 'DEU', 'Alemania', 'Germany'),
    ('DJ', 'DJI', 'Yibuti', 'Djibouti'),
    ('DK', 'DNK', 'Dinamarca', 'Denmark'),
    ('DM', 'DMA', 'Dominica', 'Dominica'),
    ('DO', 'DOM', 'República Dominicana', 'Dominican Republic'),
    ('DZ', 'DZA', 'Argelia', 'Algeria'),
    ('EC', 'ECU', 'Ecuador', 'Ecuador'),
    ('EE', 'EST', 'Estonia', 'Estonia'),
    ('EG', 'EGY', 'Egipto', 'Egypt'),
    ('EH', 'ESH', 'Sáhara Occidental', 'Western Sahara'),
    ('ER', 'ERI', 'Eritrea', 'Eritrea'),
    ('ES', 'ESP', 'España', 'Spain'),
    ('ET', 'ETH', 'Etiopía', 'Ethiopia'),
    ('FI', 'FIN', 'Finlandia', 'Finland'),
    ('FJ', 'FJI', 'Fiyi', 'Fiji'),
    ('FK', 'FLK', 'Islas Malvinas', 'Falkland Islands (Malvinas)'),
    ('FM', 'FSM', 'Micronesia', 'Micronesia, Federated States of'),
    ('FO', 'FRO', 'Islas Feroe', 'Faroe Islands'),
    ('FR', 'FRA', 'Francia', 'France'),
    ('GA', 'GAB', 'Gabón', 'Gabon'),
    ('GB', 'GBR', 'Reino Unido', 'United Kingdom'),
    ('GD', 'GRD', 'Granada', 'Grenada'),
    ('GE', 'GEO', 'Georgia', 'Georgia'),
    ('GF', 'GUF', 'Guayana Francesa', 'French Guiana'),
    ('GG', 'GGY', 'Guernesey', 'Guernsey'),
    ('GH', 'GHA', 'Ghana', 'Ghana'),
    ('GI', 'GIB', 'Gibraltar', 'Gibraltar'),
    ('GL', 'GRL', 'Groenlandia', 'Greenland'),
    ('GM', 'GMB', 'Gambia', 'Gambia'),
    ('GN', 'GIN', 'Guinea', 'Guinea'),
    ('GP', 'GLP', 'Guadalupe', 'Guadeloupe'),
    ('GQ', 'GNQ', 'Guinea Ecuatorial', 'Equatorial Guinea'),
    ('GR', 'GRC', 'Grecia', 'Greece'),
    ('GS', 'SGS', 'Islas Georgia del Sur y Sandwich del Sur', 'South Georgia and the South Sandwich Islands'),
    ('GT', 'GTM', 'Guatemala', 'Guatemala'),
    ('GU', 'GUM', 'Guam', 'Guam'),
    ('GW', 'GNB', 'Guinea-Bisáu', 'Guinea-Bissau'),
    ('GY', 'GUY', 'Guyana', 'Guyana'),
    ('HK', 'HKG', 'Hong Kong', 'Hong Kong'),
    ('HM', 'HMD', 'Islas Heard y McDonald', 'Heard Island and McDonald Islands'),
    ('HN', 'HND', 'Honduras', 'Honduras'),
    ('HR', 'HRV', 'Croacia', 'Croatia'),
    ('HT', 'HTI', 'Haití', 'Haiti'),
    ('HU', 'HUN', 'Hungría', 'Hungary'),
    ('ID', 'IDN', 'Indonesia', 'Indonesia'),
    ('IE', 'IRL', 'Irlanda', 'Ireland'),
    ('IL', 'ISR', 'Israel', 'Israel'),
    ('IM', 'IMN', 'Isla de Man', 'Isle of Man'),
    ('IN', 'IND', 'India', 'India'),
    ('IO', 'IOT', 'Territorio Británico del Océano Índico', 'British Indian Ocean Territory'),
    ('IQ', 'IRQ', 'Irak', 'Iraq'),
    ('IR', 'IRN', 'Irán', 'Iran, Islamic Republic of'),
    ('IS', 'ISL', 'Islandia', 'Iceland'),
    ('IT', 'ITA', 'Italia', 'Italy'),
    ('JE', 'JEY', 'Jersey', 'Jersey'),
    ('JM', 'JAM', 'Jamaica', 'Jamaica'),
    ('JO', 'JOR', 'Jordania', 'Jordan'),
    ('JP', 'JPN', 'Japón', 'Japan'),
    ('KE', 'KEN', 'Kenia', 'Kenya'),
    ('KG', 'KGZ', 'Kirguistán', 'Kyrgyzstan'),
    ('KH', 'KHM', 'Camboya', 'Cambodia'),
    ('KI', 'KIR', 'Kiribati', 'Kiribati'),
    ('KM', 'COM', 'Comoras', 'Comoros'),
    ('KN', 'KNA', 'San Cristóbal y Nieves', 'Saint Kitts and Nevis'),
    ('KP', 'PRK', 'Corea del Norte', "Korea, Democratic People's Republic of"),
    ('KR', 'KOR', 'Corea del Sur', 'Korea, Republic of'),
    ('KW', 'KWT', 'Kuwait', 'Kuwait'),
    ('KY', 'CYM', 'Islas Caimán', 'Cayman Islands'),
    ('KZ', 'KAZ', 'Kazajistán', 'Kazakhstan'),
    ('LA', 'LAO', 'Laos', "Lao People's Democratic Republic"),
    ('LB', 'LBN', 'Líbano', 'Lebanon'),
    ('LC', 'LCA', 'Santa Lucía', 'Saint Lucia'),
    ('LI', 'LIE', 'Liechtenstein', 'Liechtenstein'),
    ('LK', 'LKA', 'Sri Lanka', 'Sri Lanka'),
    ('LR', 'LBR', 'Liberia', 'Liberia'),
    ('LS', 'LSO', 'Lesoto', 'Lesotho'),
    ('LT', 'LTU', 'Lituania', 'Lithuania'),
    ('LU', 'LUX', 'Luxemburgo', 'Luxembourg'),
    ('LV', 'LVA', 'Letonia', 'Latvia'),
    ('LY', 'LBY', 'Libia', 'Libya'),
    ('MA', 'MAR', 'Marruecos', 'Morocco'),
    ('MC', 'MCO', 'Mónaco', 'Monaco'),
    ('MD', 'MDA', 'Moldavia', 'Moldova, Republic of'),
    ('ME', 'MNE', 'Montenegro', 'Montenegro'),
    ('MF', 'MAF', 'San Martín', 'Saint Martin (French part)'),
    ('MG', 'MDG', 'Madagascar', 'Madagascar'),
    ('MH', 'MHL', 'Islas Marshall', 'Marshall Islands'),
    ('MK', 'MKD', 'Macedonia del Norte', 'North Macedonia'),
    ('ML', 'MLI', 'Mali', 'Mali'),
    ('MM', 'MMR', 'Myanmar (Birmania)', 'Myanmar'),
    ('MN', 'MNG', 'Mongolia', 'Mongolia'),
    ('MO', 'MAC', 'Macao', 'Macao'),
    ('MP', 'MNP', 'Islas Marianas del Norte', 'Northern Mariana Islands'),
    ('MQ', 'MTQ', 'Martinica', 'Martinique'),
    ('MR', 'MRT', 'Mauritania', 'Mauritania'),
    ('MS', 'MSR', 'Montserrat', 'Montserrat'),
    ('MT', 'MLT', 'Malta', 'Malta'),
    ('MU', 'MUS', 'Mauricio', 'Mauritius'),
    ('MV', 'MDV', 'Maldivas', 'Maldives'),
    ('MW', 'MWI', 'Malaui', 'Malawi'),
    ('MX', 'MEX', 'México', 'Mexico'),
    ('MY', 'MYS', 'Malasia', 'Malaysia'),
    ('MZ', 'MOZ', 'Mozambique', 'Mozambique'),
    ('NA', 'NAM', 'Namibia', 'Namibia'),
    ('NC', 'NCL', 'Nueva Caledonia', 'New Caledonia'),
    ('NE', 'NER', 'Níger', 'Niger'),
    ('NF', 'NFK', 'Isla Norfolk', 'Norfolk Island'),
    ('NG', 'NGA', 'Nigeria', 'Nigeria'),
    ('NI', 'NIC', 'Nicaragua', 'Nicaragua'),
    ('NL', 'NLD', 'Países Bajos', 'Netherlands'),
    ('NO', 'NOR', 'Noruega', 'Norway'),
    ('NP', 'NPL', 'Nepal', 'Nepal'),
    ('NR', 'NRU', 'Nauru', 'Nauru'),
    ('NU', 'NIU', 'Niue', 'Niue'),
    ('NZ', 'NZL', 'Nueva Zelanda', 'New Zealand'),
    ('OM', 'OMN', 'Omán', 'Oman'),
    ('PA', 'PAN', 'Panamá', 'Panama'),
    ('PE', 'PER', 'Perú', 'Peru'),
    ('PF', 'PYF', 'Polinesia Francesa', 'French Polynesia'),
    ('PG', 'PNG', 'Papúa Nueva Guinea', 'Papua New Guinea'),
    ('PH', 'PHL', 'Filipinas', 'Philippines'),
    ('PK', 'PAK', 'Pakistán', 'Pakistan'),
    ('PL', 'POL', 'Polonia', 'Poland'),
    ('PM', 'SPM', 'San Pedro y Miquelón', 'Saint Pierre and Miquelon'),
    ('PN', 'PCN', 'Islas Pitcairn', 'Pitcairn'),
    ('PR', 'PRI', 'Puerto Rico', 'Puerto Rico'),
    ('PS', 'PSE', 'Palestina', 'Palestine, State of'),
    ('PT', 'PRT', 'Portugal', 'Portugal'),
    ('PW', 'PLW', 'Palaos', 'Palau'),
    ('PY', 'PRY', 'Paraguay', 'Paraguay'),
    ('QA', 'QAT', 'Catar', 'Qatar'),
    ('RE', 'REU', 'Reunión', 'Réunion'),
    ('RO', 'ROU', 'Rumanía', 'Romania'),
    ('RS', 'SRB', 'Serbia', 'Serbia'),
    ('RU', 'RUS', 'Rusia', 'Russian Federation'),
    ('RW', 'RWA', 'Ruanda', 'Rwanda'),
    ('SA', 'SAU', 'Arabia Saudí', 'Saudi Arabia'),
    ('SB', 'SLB', 'Islas Salomón', 'Solomon Islands'),
    ('SC', 'SYC', 'Seychelles', 'Seychelles'),
    ('SD', 'SDN', 'Sudán', 'Sudan'),
    ('SE', 'SWE', 'Suecia', 'Sweden'),
    ('SG', 'SGP', 'Singapur', 'Singapore'),
    ('SH', 'SHN', 'Santa Elena', 'Saint Helena, Ascension and Tristan da Cunha'),
    ('SI', 'SVN', 'Eslovenia', 'Slovenia'),
    ('SJ', 'SJM', 'Svalbard y Jan Mayen', 'Svalbard and Jan Mayen'),
    ('SK', 'SVK', 'Eslovaquia', 'Slovakia'),
    ('SL', 'SLE', 'Sierra Leona', 'Sierra Leone'),
    ('SM', 'SMR', 'San Marino', 'San Marino'),
    ('SN', 'SEN', 'Senegal', 'Senegal'),
    ('SO', 'SOM', 'Somalia', 'Somalia'),
    ('SR', 'SUR', 'Surinam', 'Suriname'),
    ('SS', 'SSD', 'Sudán del Sur', 'South Sudan'),
    ('ST', 'STP', 'Santo Tomé y Príncipe', 'Sao Tome and Principe'),
    ('SV', 'SLV', 'El Salvador', 'El Salvador'),
    ('SX', 'SXM', 'Sint Maarten', 'Sint Maarten (Dutch part)'),
    ('SY', 'SYR', 'Siria', 'Syrian Arab Republic'),
    ('SZ', 'SWZ', 'Esuatini', 'Eswatini'),
    ('TC', 'TCA', 'Islas Turcas y Caicos', 'Turks and Caicos Islands'),
    ('TD', 'TCD', 'Chad', 'Chad'),
    ('TF', 'ATF', 'Territorios Australes Franceses', 'French Southern Territories'),
    ('TG', 'TGO', 'Togo', 'Togo'),
    ('TH', 'THA', 'Tailandia', 'Thailand'),
    ('TJ', 'TJK', 'Tayikistán', 'Tajikistan'),
    ('TK', 'TKL', 'Tokelau', 'Tokelau'),
    ('TL', 'TLS', 'Timor-Leste', 'Timor-Leste'),
    ('TM', 'TKM', 'Turkmenistán', 'Turkmenistan'),
    ('TN', 'TUN', 'Túnez', 'Tunisia'),
    ('TO', 'TON', 'Tonga', 'Tonga'),
    ('TR', 'TUR', 'Turquía', 'Türkiye'),
    ('TT', 'TTO', 'Trinidad y Tobago', 'Trinidad and Tobago'),
    ('TV', 'TUV', 'Tuvalu', 'Tuvalu'),
    ('TW', 'TWN', 'Taiwán', 'Taiwan, Province of China'),
    ('TZ', 'TZA', 'Tanzania', 'Tanzania, United Republic of'),
    ('UA', 'UKR', 'Ucrania', 'Ukraine'),
    ('UG', 'UGA', 'Uganda', 'Uganda'),
    ('UM', 'UMI', 'Islas Ultramarinas Menores de Estados Unidos', 'United States Minor Outlying Islands'),
    ('US', 'USA', 'Estados Unidos', 'United States'),
    ('UY', 'URY', 'Uruguay', 'Uruguay'),
    ('UZ', 'UZB', 'Uzbekistán', 'Uzbekistan'),
    ('VA', 'VAT', 'Ciudad del Vaticano', 'Holy See (Vatican City State)'),
    ('VC', 'VCT', 'San Vicente y las Granadinas', 'Saint Vincent and the Grenadines'),
    ('VE', 'VEN', 'Venezuela', 'Venezuela, Bolivarian Republic of'),
    ('VG', 'VGB', 'Islas Vírgenes Británicas', 'Virgin Islands, British'),
    ('VI', 'VIR', 'Islas Vírgenes de Estados Unidos', 'Virgin Islands, U.S.'),
    ('VN', 'VNM', 'Vietnam', 'Viet Nam'),
    ('VU', 'VUT', 'Vanuatu', 'Vanuatu'),
    ('WF', 'WLF', 'Wallis y Futuna', 'Wallis and Futuna'),
    ('WS', 'WSM', 'Samoa', 'Samoa'),
    ('YE', 'YEM', 'Yemen', 'Yemen'),
    ('YT', 'MYT', 'Mayotte', 'Mayotte'),
    ('ZA', 'ZAF', 'Sudáfrica', 'South Africa'),
    ('ZM', 'ZMB', 'Zambia', 'Zambia'),
    ('ZW', 'ZWE', 'Zimbabue', 'Zimbabwe'),
)


def _normalizar_nombre(value):
    value = str(value or "").strip().casefold()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


class Command(BaseCommand):
    help = (
        "Carga/actualiza el catálogo ISO 3166-1 sin eliminar países "
        "existentes ni cambiar sus IDs."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Compatibilidad: fuerza modo vista previa sin persistir cambios.",
        )
        parser.add_argument(
            "--aplicar",
            action="store_true",
            help="Aplica los cambios. Sin esta opción se ejecuta como vista previa.",
        )
        parser.add_argument(
            "--confirmar",
            default="",
            help="Confirmación obligatoria: CARGAR_PAISES_ISO",
        )
        parser.add_argument(
            "--actualizar-nombres",
            action="store_true",
            help=(
                "Normaliza al español el nombre de los países ISO ya "
                "existentes. Por defecto se conserva el nombre actual."
            ),
        )

    def handle(self, *args, **options):
        aplicar = bool(options["aplicar"])
        dry_run = bool(options["dry_run"] or not aplicar)
        actualizar_nombres = bool(options["actualizar_nombres"])

        if aplicar and str(options.get("confirmar") or "").strip() != "CARGAR_PAISES_ISO":
            raise CommandError(
                "La ejecución real requiere --confirmar CARGAR_PAISES_ISO. "
                "Ejecute primero sin --aplicar para revisar la vista previa."
            )

        creados = 0
        actualizados = 0
        sin_cambios = 0
        conflictos = []

        with transaction.atomic():
            # Se reconstruye el mapa tras cada alta para que la reconciliación
            # sea estable aun cuando la base empiece parcialmente poblada.
            paises = list(Pais.objects.all().order_by("id"))

            for iso2, iso3, nombre_es, nombre_en in PAISES_ISO:
                por_iso2 = next(
                    (
                        pais
                        for pais in paises
                        if str(pais.iso2 or "").upper() == iso2
                    ),
                    None,
                )
                por_iso3 = next(
                    (
                        pais
                        for pais in paises
                        if str(pais.iso3 or "").upper() == iso3
                    ),
                    None,
                )

                if por_iso2 and por_iso3 and por_iso2.pk != por_iso3.pk:
                    conflictos.append(
                        f"{iso2}/{iso3}: ISO2 e ISO3 pertenecen a filas diferentes."
                    )
                    continue

                pais = por_iso2 or por_iso3

                if pais is None:
                    nombres_objetivo = {
                        _normalizar_nombre(nombre_es),
                        _normalizar_nombre(nombre_en),
                    }
                    coincidencias = [
                        item
                        for item in paises
                        if _normalizar_nombre(item.nombre) in nombres_objetivo
                    ]

                    if len(coincidencias) == 1:
                        pais = coincidencias[0]
                    elif len(coincidencias) > 1:
                        conflictos.append(
                            f"{iso2}/{iso3}: varias filas coinciden por nombre."
                        )
                        continue

                if pais is None:
                    pais = Pais(
                        nombre=nombre_es,
                        iso2=iso2,
                        iso3=iso3,
                    )
                    pais.save()
                    paises.append(pais)
                    creados += 1
                    continue

                cambios = []

                propietario_iso2 = next(
                    (
                        item
                        for item in paises
                        if item.pk != pais.pk
                        and str(item.iso2 or "").upper() == iso2
                    ),
                    None,
                )
                propietario_iso3 = next(
                    (
                        item
                        for item in paises
                        if item.pk != pais.pk
                        and str(item.iso3 or "").upper() == iso3
                    ),
                    None,
                )

                if propietario_iso2 or propietario_iso3:
                    conflictos.append(
                        f"{iso2}/{iso3}: códigos ocupados por otra fila."
                    )
                    continue

                if str(pais.iso2 or "").upper() != iso2:
                    pais.iso2 = iso2
                    cambios.append("iso2")

                if str(pais.iso3 or "").upper() != iso3:
                    pais.iso3 = iso3
                    cambios.append("iso3")

                if actualizar_nombres and pais.nombre != nombre_es:
                    nombre_ocupado = next(
                        (
                            item
                            for item in paises
                            if item.pk != pais.pk
                            and item.nombre.casefold() == nombre_es.casefold()
                        ),
                        None,
                    )
                    if nombre_ocupado:
                        conflictos.append(
                            f"{iso2}/{iso3}: no se renombró a '{nombre_es}' "
                            "porque ese nombre ya pertenece a otra fila."
                        )
                    else:
                        pais.nombre = nombre_es
                        cambios.append("nombre")

                if cambios:
                    pais.save(update_fields=sorted(set(cambios)))
                    actualizados += 1
                else:
                    sin_cambios += 1

            if dry_run or conflictos:
                transaction.set_rollback(True)

        if conflictos and not dry_run:
            modo = "REVERTIDO POR CONFLICTOS"
        else:
            modo = "SIMULACIÓN" if dry_run else "APLICADO"
        self.stdout.write(
            self.style.SUCCESS(
                f"{modo} · creados={creados} · actualizados={actualizados} "
                f"· sin cambios={sin_cambios} · conflictos={len(conflictos)}"
            )
        )

        if conflictos:
            self.stdout.write(self.style.WARNING("Conflictos detectados:"))
            for conflicto in conflictos:
                self.stdout.write(f"- {conflicto}")

        self.stdout.write(
            "No se eliminó ningún país existente y no se modificó ningún ID."
        )

        if conflictos and not dry_run:
            raise CommandError(
                "La operación fue revertida porque se detectaron conflictos. "
                "Corríjalos y ejecute nuevamente el comando."
            )

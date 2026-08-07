from django.core.exceptions import ValidationError
from django.db import models


def _norm_text(value):
    """
    Normaliza valores de texto eliminando espacios
    al inicio y al final.
    """
    return str(value or "").strip()


class AreaConocimiento(models.Model):
    """
    Área amplia del conocimiento según la clasificación CINE-F.

    Ejemplos:
    - 01 -> Educación
    - 05 -> Ciencias naturales, matemáticas y estadística
    - 06 -> Tecnologías de la información y la comunicación (TIC)
    """

    codigo = models.CharField(
        max_length=2,
        unique=True,
    )

    nombre = models.CharField(
        max_length=150,
        unique=True,
    )

    class Meta:
        db_table = "areas_conocimiento"
        ordering = [
            "codigo",
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.codigo = _norm_text(
            self.codigo
        )

        self.nombre = _norm_text(
            self.nombre
        )

        # =====================================================
        # VALIDACIÓN DEL CÓDIGO
        # =====================================================

        if not self.codigo:
            errors["codigo"] = (
                "El código del área es obligatorio."
            )

        elif (
            len(self.codigo) != 2
            or not self.codigo.isdigit()
        ):
            errors["codigo"] = (
                "El código del área debe contener "
                "exactamente 2 dígitos."
            )

        # =====================================================
        # VALIDACIÓN DEL NOMBRE
        # =====================================================

        if not self.nombre:
            errors["nombre"] = (
                "El nombre del área es obligatorio."
            )

        if errors:
            raise ValidationError(
                errors
            )

    def save(
        self,
        *args,
        **kwargs,
    ):
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        """
        Se muestra únicamente el nombre.

        El código CINE-F se conserva internamente
        como dato estructurado del catálogo.
        """
        return self.nombre


class Subarea(models.Model):
    """
    Subárea del conocimiento asociada a un área CINE-F.

    Ejemplo:

    Área:
        05 -> Ciencias naturales, matemáticas y estadística

    Subáreas:
        051 -> Ciencias biológicas y afines
        052 -> Medio ambiente
        053 -> Ciencias físicas
        054 -> Matemáticas y estadística
    """

    codigo = models.CharField(
        max_length=3,
        unique=True,
    )

    nombre = models.CharField(
        max_length=150,
    )

    area = models.ForeignKey(
        AreaConocimiento,
        on_delete=models.PROTECT,
        related_name="subareas",
    )

    class Meta:
        db_table = "subareas_conocimiento"

        ordering = [
            "codigo",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "nombre",
                    "area",
                ],
                name="unique_subarea_por_area",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "area",
                    "nombre",
                ],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.codigo = _norm_text(
            self.codigo
        )

        self.nombre = _norm_text(
            self.nombre
        )

        # =====================================================
        # VALIDACIÓN DEL CÓDIGO
        # =====================================================

        if not self.codigo:
            errors["codigo"] = (
                "El código de la subárea es obligatorio."
            )

        elif (
            len(self.codigo) != 3
            or not self.codigo.isdigit()
        ):
            errors["codigo"] = (
                "El código de la subárea debe contener "
                "exactamente 3 dígitos."
            )

        # =====================================================
        # VALIDACIÓN DEL NOMBRE
        # =====================================================

        if not self.nombre:
            errors["nombre"] = (
                "El nombre de la subárea es obligatorio."
            )

        # =====================================================
        # VALIDACIÓN DEL ÁREA
        # =====================================================

        if not self.area_id:
            errors["area"] = (
                "El área es obligatoria."
            )

        # =====================================================
        # VALIDACIÓN DE LA JERARQUÍA CINE-F
        # =====================================================
        #
        # Ejemplo válido:
        #
        # Área:    05
        # Subárea: 051
        #
        # Ejemplo inválido:
        #
        # Área:    06
        # Subárea: 091
        #
        # Los dos primeros dígitos de la subárea deben
        # corresponder al código del área seleccionada.
        # =====================================================

        if (
            self.codigo
            and self.area_id
        ):
            area_codigo = _norm_text(
                getattr(
                    self.area,
                    "codigo",
                    "",
                )
            )

            if (
                area_codigo
                and not self.codigo.startswith(
                    area_codigo
                )
            ):
                errors["codigo"] = (
                    "El código de la subárea no corresponde "
                    "al área seleccionada."
                )

        if errors:
            raise ValidationError(
                errors
            )

    def save(
        self,
        *args,
        **kwargs,
    ):
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        """
        Se muestra únicamente el nombre.

        El código y el área padre permanecen como
        información estructurada del catálogo.
        """
        return self.nombre
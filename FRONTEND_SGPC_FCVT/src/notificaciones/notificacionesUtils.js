import {
  tipoNotificacionLabel,
} from "../scripts/api/notificacionesApi";

const REVIEW_TYPES = new Set([
  "publicacion_enviada",
  "publicacion_observada",
  "publicacion_aprobada",
  "publicacion_rechazada",
  "nueva_publicacion_revision",
  "publicacion_reenviada",
]);

const ADMIN_REVIEW_TYPES =
  new Set([
    "nueva_publicacion_revision",
    "publicacion_reenviada",
  ]);

const PROFILE_EXTENSION_TYPES = new Set([
  "solicitud_extension_perfil",
  "extension_perfil_aprobada",
  "extension_perfil_rechazada",
]);

const DATA_UPDATE_TYPES = new Set([
  "campania_actualizacion",
  "recordatorio_actualizacion",
]);

const PUBLICATION_CHANGE_REQUEST_TYPES = new Set([
  "solicitud_modificacion_publicacion",
  "modificacion_publicacion_aprobada",
  "modificacion_publicacion_rechazada",
]);

const toText = (
  value
) =>
  String(value ?? "").trim();

const normalizeType = (
  value
) =>
  toText(value).toLowerCase();

const shorten = (
  value,
  maxLength = 150
) => {
  const text = toText(value);

  if (
    !text ||
    text.length <= maxLength
  ) {
    return text;
  }

  return `${text
    .slice(0, maxLength - 1)
    .trimEnd()}…`;
};

const publicationTitle = (
  notification
) =>
  toText(
    notification?.publicacion_titulo
  );

const publicationType = (
  notification
) =>
  toText(
    notification?.publicacion_tipo
  );

const publicationSubject = (
  notification
) => {
  const title = shorten(
    publicationTitle(notification)
  );

  if (title) {
    return `“${title}”`;
  }

  const type = publicationType(
    notification
  );

  return "La publicación";
};

export const notificationTypeLabel = (
  notification
) => {
  const mappedLabel =
    tipoNotificacionLabel(
      notification?.tipo
    );

  if (
    mappedLabel &&
    mappedLabel !== "Notificación"
  ) {
    return mappedLabel;
  }

  return (
    toText(
      notification?.tipo_label
    ) || "Notificación"
  );
};

export const notificationPresentation = (
  notification
) => {
  const type = normalizeType(
    notification?.tipo
  );

  const subject =
    publicationSubject(
      notification
    );

  const pubType =
    publicationType(
      notification
    );

  switch (type) {
    case "publicacion_enviada":
      return {
        title: "Enviada a revisión",
        message:
          `${subject} está siendo revisada. ` +
          "No podrá editarla mientras permanezca en revisión.",
        meta: pubType,
      };

    case "publicacion_observada":
      return {
        title: "Correcciones solicitadas",
        message:
          `${subject} tiene observaciones. ` +
          "Revise los comentarios y realice los ajustes solicitados.",
        meta: pubType,
      };

    case "publicacion_aprobada":
      return {
        title: "Publicación aprobada",
        message:
          `${subject} fue aprobada.`,
        meta: pubType,
      };

    case "publicacion_rechazada":
      return {
        title: "Publicación rechazada",
        message:
          `${subject} fue rechazada. Revise el motivo ` +
          "registrado en el detalle de la publicación.",
        meta: pubType,
      };

    case "nueva_publicacion_revision":
      return {
        title: "Nueva publicación para revisar",
        message:
          `${subject} está lista para revisión.`,
        meta: pubType,
      };

    case "publicacion_reenviada":
      return {
        title:
          "Publicación reenviada para revisión",
        message:
          `${subject} fue reenviada después de recibir observaciones.`,
        meta: pubType,
      };

    case "solicitud_extension_perfil":
      return {
        title: "Solicitud de extensión de perfil",
        message:
          toText(notification?.mensaje) ||
          "Un usuario solicita más tiempo para editar su perfil.",
        meta: "Gestión de usuarios",
      };

    case "extension_perfil_aprobada":
      return {
        title: "Extensión de perfil aprobada",
        message:
          toText(notification?.mensaje) ||
          "Su solicitud de extensión fue aprobada.",
        meta: "Perfil",
      };

    case "extension_perfil_rechazada":
      return {
        title: "Solicitud de extensión rechazada",
        message:
          toText(notification?.mensaje) ||
          "Su solicitud de extensión fue rechazada.",
        meta: "Perfil",
      };

    case "campania_actualizacion":
      return {
        title: "Actualización de información requerida",
        message:
          toText(notification?.mensaje) ||
          "Tiene información pendiente por revisar en el SGPC.",
        meta: "Actualización de datos",
      };

    case "recordatorio_actualizacion":
      return {
        title: "Recordatorio de actualización",
        message:
          toText(notification?.mensaje) ||
          "Aún tiene información pendiente por completar.",
        meta: "Actualización de datos",
      };

    case "solicitud_modificacion_publicacion":
      return {
        title: "Solicitud de modificación",
        message:
          toText(notification?.mensaje) ||
          `${subject} tiene una solicitud de modificación pendiente.`,
        meta: pubType || "Publicaciones",
      };

    case "modificacion_publicacion_aprobada":
      return {
        title: "Modificación aprobada",
        message:
          toText(notification?.mensaje) ||
          `Los cambios autorizados de ${subject} ya fueron aplicados.`,
        meta: pubType || "Publicaciones",
      };

    case "modificacion_publicacion_rechazada":
      return {
        title: "Modificación rechazada",
        message:
          toText(notification?.mensaje) ||
          `La solicitud de modificación de ${subject} fue rechazada.`,
        meta: pubType || "Publicaciones",
      };

    default:
      return {
        title:
          toText(
            notification?.titulo
          ) ||
          notificationTypeLabel(
            notification
          ),
        message:
          toText(
            notification?.mensaje
          ) ||
          "Tiene una nueva notificación.",
        meta: pubType,
      };
  }
};

export const notificationTone = (
  type
) => {
  switch (
    normalizeType(type)
  ) {
    case "publicacion_aprobada":
    case "extension_perfil_aprobada":
    case "modificacion_publicacion_aprobada":
      return "success";

    case "publicacion_observada":
    case "solicitud_extension_perfil":
    case "recordatorio_actualizacion":
    case "solicitud_modificacion_publicacion":
      return "warning";

    case "publicacion_rechazada":
    case "extension_perfil_rechazada":
    case "modificacion_publicacion_rechazada":
      return "danger";

    default:
      return "info";
  }
};

export const notificationIconPath = (
  type
) => {
  switch (
    normalizeType(type)
  ) {
    case "publicacion_aprobada":
      return "M9.55 18 3.85 12.3l1.4-1.4 4.3 4.3 9.2-9.2 1.4 1.4L9.55 18Z";

    case "publicacion_observada":
      return "M11 17h2v2h-2v-2Zm0-12h2v10h-2V5Zm1-3a10 10 0 1 0 0 20 10 10 0 0 0 0-20Z";

    case "publicacion_rechazada":
      return "m7.76 6.34 4.24 4.24 4.24-4.24 1.42 1.42L13.42 12l4.24 4.24-1.42 1.42L12 13.42l-4.24 4.24-1.42-1.42L10.58 12 6.34 7.76l1.42-1.42Z";

    case "publicacion_reenviada":
      return "M12 4V1l4 4-4 4V6a6 6 0 1 0 5.65 8H20a8 8 0 1 1-8-10Z";

    case "solicitud_extension_perfil":
      return "M12 2a7 7 0 0 0-7 7v3.1L3.3 15a1 1 0 0 0 .86 1.5h15.68a1 1 0 0 0 .86-1.5L19 12.1V9a7 7 0 0 0-7-7Zm-1 17h2v2h-2v-2Zm1-14a4 4 0 0 1 4 4v3.7l.7 1.3H7.3l.7-1.3V9a4 4 0 0 1 4-4Z";

    case "extension_perfil_aprobada":
      return "M9.55 18 3.85 12.3l1.4-1.4 4.3 4.3 9.2-9.2 1.4 1.4L9.55 18Z";

    case "extension_perfil_rechazada":
      return "m7.76 6.34 4.24 4.24 4.24-4.24 1.42 1.42L13.42 12l4.24 4.24-1.42 1.42L12 13.42l-4.24 4.24-1.42-1.42L10.58 12 6.34 7.76l1.42-1.42Z";

    default:
      return "M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h8v2H8v-2Zm0 4h5v2H8v-2Z";
  }
};

export const formatNotificationDate = (
  value
) => {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "";
  }

  const now = new Date();
  const diff =
    now.getTime() -
    date.getTime();

  if (
    diff >= 0 &&
    diff < 60_000
  ) {
    return "Ahora";
  }

  if (
    diff >= 0 &&
    diff < 3_600_000
  ) {
    const minutes =
      Math.max(
        1,
        Math.floor(
          diff / 60_000
        )
      );

    return `Hace ${minutes} min`;
  }

  if (
    diff >= 0 &&
    diff < 86_400_000
  ) {
    const hours =
      Math.max(
        1,
        Math.floor(
          diff / 3_600_000
        )
      );

    return `Hace ${hours} h`;
  }

  return new Intl.DateTimeFormat(
    "es-EC",
    {
      day: "2-digit",
      month: "short",
      year:
        date.getFullYear() !==
        now.getFullYear()
          ? "numeric"
          : undefined,
      hour: "2-digit",
      minute: "2-digit",
    }
  ).format(date);
};

export const isWorkflowNotification = (
  type
) =>
  REVIEW_TYPES.has(
    normalizeType(type)
  );

export const isProfileExtensionNotification = (
  notification
) => PROFILE_EXTENSION_TYPES.has(
  normalizeType(notification?.tipo)
);

export const notificationHasAction = (
  notification
) => Boolean(
  Number(notification?.publicacion_id) > 0 ||
  Number(notification?.metadata?.solicitud_extension_id) > 0 ||
  Number(notification?.metadata?.solicitud_modificacion_id) > 0 ||
  PROFILE_EXTENSION_TYPES.has(
    normalizeType(notification?.tipo)
  ) ||
  DATA_UPDATE_TYPES.has(
    normalizeType(notification?.tipo)
  ) ||
  PUBLICATION_CHANGE_REQUEST_TYPES.has(
    normalizeType(notification?.tipo)
  )
);

export const notificationActionLabel = (
  notification,
  {
    isAdmin = false,
  } = {}
) => {
  const type = normalizeType(
    notification?.tipo
  );

  if (
    isAdmin &&
    type === "solicitud_extension_perfil"
  ) {
    return "Revisar solicitud";
  }

  if (
    isAdmin &&
    type === "solicitud_modificacion_publicacion"
  ) {
    return "Revisar solicitud";
  }

  if (DATA_UPDATE_TYPES.has(type)) {
    return "Completar información";
  }

  if (
    type === "modificacion_publicacion_aprobada" ||
    type === "modificacion_publicacion_rechazada"
  ) {
    return "Ver publicación";
  }

  if (
    type === "extension_perfil_aprobada" ||
    type === "extension_perfil_rechazada"
  ) {
    return "Ver perfil";
  }

  if (
    isAdmin &&
    ADMIN_REVIEW_TYPES.has(type)
  ) {
    return "Revisar publicación";
  }

  switch (type) {
    case "publicacion_observada":
      return "Ver observaciones";

    case "publicacion_enviada":
      return "Ver estado";

    default:
      return "Ver publicación";
  }
};

export const notificationTarget = (
  notification,
  {
    isAdmin = false,
  } = {}
) => {
  const type = normalizeType(
    notification?.tipo
  );

  if (DATA_UPDATE_TYPES.has(type)) {
    return "/informacion-pendiente";
  }

  if (
    isAdmin &&
    type === "solicitud_modificacion_publicacion"
  ) {
    return "/admin/solicitudes-modificacion-publicaciones";
  }

  if (
    type === "solicitud_extension_perfil" &&
    isAdmin &&
    Number(notification?.metadata?.solicitud_extension_id) > 0
  ) {
    // NotificacionesView intercepta este destino y deriva la gestión a Administración → Usuarios.
    return "/notificaciones";
  }

  if (
    type === "extension_perfil_aprobada" ||
    type === "extension_perfil_rechazada"
  ) {
    return "/perfil";
  }

  const publicationId =
    Number(
      notification
        ?.publicacion_id
    );

  if (
    !Number.isInteger(
      publicationId
    ) ||
    publicationId < 1
  ) {
    return "/notificaciones";
  }

  if (
    isAdmin &&
    ADMIN_REVIEW_TYPES.has(type)
  ) {
    return `/admin/revision/${publicationId}`;
  }

  return `/publicacion/${publicationId}`;
};

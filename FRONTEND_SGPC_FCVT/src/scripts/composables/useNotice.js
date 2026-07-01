import { reactive } from "vue";

export function useNotice() {
  const notice = reactive({
    open: false,
    title: "",
    message: "",
    details: null,
    confirm: false,
    confirmText: "Confirmar",
    cancelText: "Cancelar",
    onConfirm: null,
    onCancel: null,
  });

  const openNotice = ({
    title,
    message,
    details = null,
    confirm = false,
    confirmText = "Confirmar",
    cancelText = "Cancelar",
    onConfirm = null,
    onCancel = null,
  } = {}) => {
    notice.title = title || "Aviso";
    notice.message = message || "";
    notice.details = details;
    notice.confirm = !!confirm;
    notice.confirmText = confirmText || "Confirmar";
    notice.cancelText = cancelText || "Cancelar";
    notice.onConfirm = typeof onConfirm === "function" ? onConfirm : null;
    notice.onCancel = typeof onCancel === "function" ? onCancel : null;
    notice.open = true;
  };

  const closeNotice = () => {
    notice.open = false;
    notice.confirm = false;
    notice.onConfirm = null;
    notice.onCancel = null;
    notice.details = null;
  };

  return {
    notice,
    openNotice,
    closeNotice,
  };
}
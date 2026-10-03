import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
} from 'react';
import { useNavigate } from 'react-router-dom';

export const ASSISTANT_OPEN_EVENT = 'millmitra:assistant-open';

const AssistantContext = createContext({
  registerFill: () => () => {},
  registerOpen: () => () => {},
  applyActions: async () => ({ filled: [], missing: [] }),
});

const wait = (ms) => new Promise((resolve) => {
  window.setTimeout(resolve, ms);
});

function inferFillTarget(fields, hint) {
  if (hint) return hint;
  if (!fields) return 'register-farmer';
  if (fields.fullName || fields.fatherName || fields.phone || fields.email || fields.village) {
    return 'register-farmer';
  }
  if (fields.variety || fields.product || fields.location) {
    return 'add-stock';
  }
  return hint || 'register-farmer';
}

export function AssistantProvider({ children }) {
  const navigate = useNavigate();
  const fillRef = useRef(new Map());
  const openRef = useRef(new Map());

  const registerFill = useCallback((target, handler) => {
    if (!target || typeof handler !== 'function') return () => {};
    fillRef.current.set(target, handler);
    return () => {
      if (fillRef.current.get(target) === handler) {
        fillRef.current.delete(target);
      }
    };
  }, []);

  const registerOpen = useCallback((target, handler) => {
    if (!target || typeof handler !== 'function') return () => {};
    openRef.current.set(target, handler);
    return () => {
      if (openRef.current.get(target) === handler) {
        openRef.current.delete(target);
      }
    };
  }, []);

  const openTarget = useCallback((target) => {
    const handler = openRef.current.get(target);
    if (handler) {
      handler();
      return true;
    }
    window.dispatchEvent(new CustomEvent(ASSISTANT_OPEN_EVENT, { detail: { target } }));
    return Boolean(openRef.current.get(target));
  }, []);

  const applyFill = useCallback(async (target, fields) => {
    if (!target || !fields || Object.keys(fields).length === 0) return false;
    const tryFill = () => {
      const handler = fillRef.current.get(target);
      if (!handler) return false;
      handler(fields);
      return true;
    };
    if (tryFill()) return true;
    openTarget(target);
    for (let attempt = 0; attempt < 10; attempt += 1) {
      await wait(60);
      if (tryFill()) return true;
    }
    return false;
  }, [openTarget]);

  const applyActions = useCallback(async (actions) => {
    const result = { filled: [], missing: [], opened: [], navigated: [] };
    const list = Array.isArray(actions) ? actions : [];
    let lastOpen = '';

    for (const action of list) {
      if (!action || typeof action !== 'object') continue;
      if (action.type === 'navigate' && action.path) {
        navigate(action.path);
        result.navigated.push(action.path);
        await wait(80);
      } else if (action.type === 'open' && action.target) {
        lastOpen = action.target;
        openTarget(action.target);
        result.opened.push(action.target);
        await wait(80);
      } else if (action.type === 'fill' && action.fields) {
        const target = inferFillTarget(action.fields, action.target || lastOpen);
        const ok = await applyFill(target, action.fields);
        if (ok) result.filled.push(target);
        else result.missing.push(target);
      }
    }
    return result;
  }, [applyFill, navigate, openTarget]);

  const value = useMemo(() => ({
    registerFill,
    registerOpen,
    applyActions,
  }), [applyActions, registerFill, registerOpen]);

  return (
    <AssistantContext.Provider value={value}>
      {children}
    </AssistantContext.Provider>
  );
}

export function useAssistant() {
  return useContext(AssistantContext);
}

export function useAssistantFill(target, handler, enabled = true) {
  const { registerFill } = useAssistant();
  const handlerRef = useRef(handler);
  handlerRef.current = handler;
  useEffect(() => {
    if (!enabled) return undefined;
    return registerFill(target, (fields) => handlerRef.current?.(fields));
  }, [enabled, registerFill, target]);
}

export function useAssistantOpen(target, handler) {
  const { registerOpen } = useAssistant();
  const handlerRef = useRef(handler);
  handlerRef.current = handler;
  useEffect(() => {
    const unregister = registerOpen(target, () => handlerRef.current?.());
    const onEvent = (event) => {
      if (event.detail?.target === target) handlerRef.current?.();
    };
    window.addEventListener(ASSISTANT_OPEN_EVENT, onEvent);
    return () => {
      unregister();
      window.removeEventListener(ASSISTANT_OPEN_EVENT, onEvent);
    };
  }, [registerOpen, target]);
}

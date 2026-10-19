// Iconos de línea (SVG) compartidos por todas las pantallas. Uso: Ico.camion, Ico.usuario, ...
const Ico = (() => {
  const mk = (d, extra = "") =>
    `<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${d}</svg>`;
  return {
    inicio: mk('<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>'),
    grafica: mk('<path d="M3 3v18h18"/><path d="M6.5 15l4-5 3.5 3.5L20 7"/>'),
    camion: mk('<path d="M2.5 6.5h11v9h-11z"/><path d="M13.5 9.5h4l3 3.5v2.5h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>'),
    dinero: mk('<circle cx="12" cy="12" r="9"/><path d="M14.8 9.2c-.5-1-1.5-1.5-2.8-1.5-1.6 0-2.7.8-2.7 2 0 1.3 1.2 1.8 2.7 2.2 1.6.4 2.8.9 2.8 2.3 0 1.2-1.2 2-2.8 2-1.4 0-2.4-.6-2.9-1.6M12 6v1.7M12 16.3V18"/>'),
    rayo: mk('<path d="M13 2.5L5 13.5h6l-1 8 8-11h-6z"/>'),
    barras: mk('<rect x="4" y="12" width="4" height="8" rx="1"/><rect x="10" y="4" width="4" height="16" rx="1"/><rect x="16" y="9" width="4" height="11" rx="1"/>'),
    buscar: mk('<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>'),
    campana: mk('<path d="M6 16.5V11a6 6 0 1 1 12 0v5.5l1.5 2h-15z"/><path d="M10 21h4"/>'),
    salir: mk('<path d="M9 4.5H5.5a1 1 0 0 0-1 1v13a1 1 0 0 0 1 1H9"/><path d="M15 8l4 4-4 4M19 12H9"/>'),
    flecha: mk('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    chevron: mk('<path d="M9 6l6 6-6 6"/>'),
    chevronAbajo: mk('<path d="M6 9l6 6 6-6"/>'),
    usuario: mk('<circle cx="12" cy="8" r="4"/><path d="M4.5 20c.8-3.6 3.7-5.5 7.5-5.5s6.7 1.9 7.5 5.5"/>'),
    candado: mk('<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>'),
    ojo: mk('<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/>'),
    ojoCerrado: mk('<path d="M3 3l18 18M10.6 6c.45-.1.9-.15 1.4-.15 6 0 9.5 6.15 9.5 6.15a16 16 0 0 1-2.7 3.4M6.6 7.6A16.5 16.5 0 0 0 2.5 12S6 18.15 12 18.15c1.5 0 2.8-.4 4-.95"/><path d="M9.9 9.9a3.3 3.3 0 0 0 4.2 4.2"/>'),
    subir: mk('<path d="M12 19V5M6 11l6-6 6 6"/>'),
    bajar: mk('<path d="M12 5v14M6 13l6 6 6-6"/>'),
    menu: mk('<path d="M4 7h16M4 12h16M4 17h16"/>'),
    cerrar: mk('<path d="M6 6l12 12M18 6L6 18"/>'),
    engranaje: mk('<circle cx="12" cy="12" r="3"/><path d="M19.4 14a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V20a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H4a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3h0a1.6 1.6 0 0 0 1-1.5V4a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8v0a1.6 1.6 0 0 0 1.5 1H20a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z"/>'),
  };
})();

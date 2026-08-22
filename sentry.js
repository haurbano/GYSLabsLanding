(() => {
  if (!window.Sentry) return;

  window.Sentry.init({
    dsn: "https://8e1819eb9e57439a9646594844642670@ingest.haurtech.com/5",
    sendDefaultPii: false,
    tracesSampleRate: 0,
    autoSessionTracking: false,
    maxBreadcrumbs: 0,
    beforeBreadcrumb: () => null,
    beforeSend(event) {
      delete event.request;
      delete event.breadcrumbs;
      delete event.user;
      delete event.extra;
      for (const exception of event.exception?.values || []) {
        exception.value = exception.type || "Error";
      }
      return event;
    },
  });
})();

(function () {
    let data = {};
  
    function post(payload) {
      fetch(`/scorm/runtime/${window.sco_id}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });
    }
  
    const API = {
      LMSInitialize() { return "true"; },
      LMSFinish() { post({ "lesson_status": data.lesson_status || "completed" }); return "true"; },
      LMSSetValue(k, v) { data[k] = v; return "true"; },
      LMSCommit() { post(data); return "true"; },
      LMSGetValue(k) { return data[k] || ""; },
      LMSGetLastError() { return "0"; },
      LMSGetErrorString() { return "OK"; },
      LMSGetDiagnostic() { return ""; },
    };
  
    window.API = API; // SCORM 1.2
  })();
// Frontend JS to fetch and display leads and add new leads
document.addEventListener("DOMContentLoaded", () => {
  const leadsTBody = document.querySelector("#leads-table tbody");
  const btnRefresh = document.querySelector("#btn-refresh");
  const btnNew = document.querySelector("#btn-new");
  const modal = document.getElementById("modal");
  const saveBtn = document.getElementById("save-lead");
  const cancelBtn = document.getElementById("cancel-lead");

  async function loadLeads(){
    leadsTBody.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";
    try{
      const res = await fetch("/api/leads");
      if(res.status === 401){
        window.location = "/login";
        return;
      }
      const data = await res.json();
      if(!Array.isArray(data)){
        leadsTBody.innerHTML = "<tr><td colspan='5'>No leads</td></tr>";
        return;
      }
      if(data.length === 0) leadsTBody.innerHTML = "<tr><td colspan='5'>No leads</td></tr>";
      else {
        leadsTBody.innerHTML = data.map(l => `<tr>
          <td>${l.id}</td><td>${escapeHtml(l.name)}</td><td>${escapeHtml(l.email||"")}</td><td>${escapeHtml(l.company||"")}</td><td>${escapeHtml(l.status||"")}</td>
        </tr>`).join("");
      }
    }catch(e){
      leadsTBody.innerHTML = "<tr><td colspan='5'>Error loading leads</td></tr>";
      console.error(e);
    }
  }

  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m]));
  }

  btnRefresh?.addEventListener("click", loadLeads);
  btnNew?.addEventListener("click", () => { modal.classList.remove("hidden"); });

  cancelBtn?.addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  saveBtn?.addEventListener("click", async () => {
    const name = document.getElementById("lead-name").value.trim();
    const email = document.getElementById("lead-email").value.trim();
    const company = document.getElementById("lead-company").value.trim();
    const status = document.getElementById("lead-status").value;
    if(!name){ alert("Name required"); return; }
    try{
      const res = await fetch("/api/leads", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({name,email,company,status})
      });
      if(res.status === 201){
        modal.classList.add("hidden");
        document.getElementById("lead-name").value = "";
        document.getElementById("lead-email").value = "";
        document.getElementById("lead-company").value = "";
        await loadLeads();
      } else {
        const err = await res.json();
        alert(err.error || "Could not save");
      }
    }catch(e){
      alert("Network error");
    }
  });

  // initial load
  loadLeads();
});

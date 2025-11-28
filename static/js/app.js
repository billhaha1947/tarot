const socket = io();
socket.on("oracle_token", d=>{
  const el=document.getElementById("ai-stream");
  el.innerText+=d.t;
});

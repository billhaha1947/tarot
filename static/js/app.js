const socket = io();
const box = document.getElementById("msgBox");
const input = document.getElementById("input");
const btn = document.getElementById("sendBtn");
const typing = document.getElementById("typing");

function addBubble(text,user){
  const d=document.createElement("div");
  d.className=user?"bubble user":"bubble ai glass";
  d.innerText=text;
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}

let stream="";
socket.on("stream",(tk)=>{
  typing.style.display="none";
  stream+=tk;
  if(!window.aiDiv){
    aiDiv=document.createElement("div");
    aiDiv.className="bubble ai glass"; box.appendChild(aiDiv);
  }
  aiDiv.innerText=stream;
  box.scrollTop=box.scrollHeight;
});

socket.on("typing",()=>typing.style.display="block");

socket.on("oracle_json",(o)=>{
  const h=document.createElement("div");
  h.className="p-3 mt-3 glass neon-glow rounded-2xl";
  h.innerHTML=`
    <div class="text-xl">${o.emoji} ${o.tarot_card}</div>
    <div>🍀 May mắn: ${o.luck_pct}%</div>
    <div>🔢 Số: ${o.lucky_numbers.join(", ")}</div>
    <div>💬 Lời khuyên: ${o.advice}</div>
    <div class="text-xs mt-2 opacity-80">3 lá: ${o.three.past} → ${o.three.present} → ${o.three.future}</div>
    ${o.symbols.map(s=>`<div class='text-[10px]'>🔍 ${s.symbol}: ${s.meaning}</div>`).join("")}
  `;
  box.appendChild(h); box.scrollTop=box.scrollHeight;
});

btn.onclick=()=>{
  stream="";
  window.aiDiv=null;
  const t=input.value.trim(); if(!t) return;
  socket.emit("prompt",{text:t});
  addBubble(t,true);
  input.value="";
};

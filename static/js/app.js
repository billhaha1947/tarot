const socket = io();
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("chat-input");
const sidebar = document.getElementById("convo-list");

document.getElementById("new-chat").onclick = ()=>{
    chatBox.innerHTML="";
};

input.onkeydown = (e)=>{
    if(e.key==="Enter"){
        const text = input.value.trim();
        if(!text) return;
        chatBox.innerHTML += `
        <div class="text-right mb-3">
            <div class="inline-block rounded-2xl px-4 py-2 bg-purple-900 text-white glow">${text}</div>
        </div>`;
        socket.emit("generate_reply",{prompt:text});
        input.value="";
    }
};

socket.on("typing",(d)=>{
    const t = document.getElementById("typing");
    t.style.display = d.status ? "block":"none";
});

socket.on("stream",(d)=>{
    chatBox.innerHTML += `
    <div class="text-left mb-3">
        <div class="inline-block rounded-2xl px-4 py-2 bg-black text-green-400 glass">${d.token}</div>
    </div>`;
});

socket.on("oracle_json",(data)=>{
    sidebar.innerHTML += `
    <div class="p-3 glass rounded-xl border border-purple-500 mb-2">${data.tarot_card} ${data.emoji}</div>`;
});

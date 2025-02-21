document.addEventListener("DOMContentLoaded", function () {
  const socket = io();
  const messageForm = document.getElementById("message-form");
  const messageInput = document.getElementById("message-input");
  const messages = document.getElementById("messages");

  messageForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const message = messageInput.value;
    if (message.trim() !== "") {
      socket.emit("send_message", { message: message });
      messageInput.value = "";
    }
  });

  socket.on("receive_message", function (data) {
    const messageElement = document.createElement("div");
    messageElement.className = "message";
    messageElement.innerHTML = `<p>${data.message}</p>`;
    messages.appendChild(messageElement);
    messages.scrollTop = messages.scrollHeight;
  });
});

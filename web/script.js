// Use WebSocket transport endpoint.
const client = new Centrifuge('ws://127.0.0.1:8080/centrifugo/connection/websocket', {
   data: {
      username: "root",
      password: "password"
   }
});

// Trigger actual connection establishement.
client.connect();

var username = ""

const inUsername = document.getElementById("inUsername")
const inChannel = document.getElementById("inChannel")
const inMessage = document.getElementById("inMessage")

const output = document.getElementById("output")

const btnSubscribe = document.getElementById("btnSubscribe")
const btnPublish = document.getElementById("btnPublish")

btnSubscribe.addEventListener("click", () =>
{
   if (inUsername != "" && inChannel.value != "")
   {
      username = inUsername.value

      const sub = client.newSubscription(inChannel.value)

      sub.on("publication", (msg) =>
      {
         let line = `<p><strong>${msg.data.from}:</strong> ${msg.data.message}</p>`
         output.innerHTML += line
      })

      sub.subscribe()
   }
})

btnPublish.addEventListener("click", () =>
{
   if (inMessage.value != "")
   {
      client.publish(inChannel.value, {
         from: username,
         message: inMessage.value
      })

      inMessage.value = ""
   }
})
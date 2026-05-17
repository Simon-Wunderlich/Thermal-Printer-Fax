import { useEffect, useState } from "react";
import "./App.css";
import mqtt from "mqtt";

function App() {
  const [msg, setMsg] = useState("");
  const key = "70656e6973";

  const client = mqtt.connect("tls://broker.hivemq.com:8884");

  client.on("connect", () => {
    console.log("i am working");
    client.publish(key + "/all", "Hello mqtt");
  });

  client.on("message", (topic, message) => {
    // message is Buffer
    console.log(message.toString());
    client.end();
  });

  const sendMessage = () => {
    client.publish(key + "/all", msg);
  };

  return (
    <>
      <form onSubmit={sendMessage}>
        <input onChange={(event) => setMsg(event.target.value)} />
        <p>{msg}</p>
        <button type={"submit"}>Send!</button>
      </form>
    </>
  );
}

export default App;

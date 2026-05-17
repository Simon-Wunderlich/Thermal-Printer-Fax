import { useEffect, useState, useRef } from "react";
import "./App.css";
import Paho from "paho-mqtt";

function App() {
  const [msg, setMsg] = useState("");
  const clientRef = useRef(null);
  const input = useRef(null)

  useEffect(() => {
    // 1. Initialize the Client
    const client = new Paho.Client(
      "broker.hivemq.com", // Replace with your MQTT broker address
      8000,
      "react-client-id",
    );

    // 2. Setup Callbacks
    client.onConnectionLost = (responseObject) => {
      console.log("Connection Lost: " + responseObject.errorMessage);
    };

    // 3. Connect to the Broker
    client.connect({
      onSuccess: () => {
        console.log("Connected to MQTT Broker");
        // 4. Subscribe after connecting
        client.subscribe("70656e6973/all");
      },
      onFailure: (message) => {
        console.log("Connection Failed: " + message.errorMessage);
      },
    });

    clientRef.current = client;
    // 5. Cleanup on unmount
    return () => {
      if (clientRef.current && clientRef.current.isConnected()) {
        clientRef.current.disconnect();
      }
    };
  }, []);

  // Function to Publish Messages
  const sendMessage = (e) => {
    e.preventDefault();
    if (msg == "")
      return
    if (clientRef.current && clientRef.current.isConnected()) {
      const message = new Paho.Message(msg);
      message.destinationName = "70656e6973/all";
      clientRef.current.send(message);
      setMsg("");
      input.current.value = ""
    }
  };
  return (
    <>
      <form onSubmit={sendMessage}>
        <input onChange={(event) => setMsg(event.target.value)} ref={input}/>
        <p>{msg}</p>
        <button type={"submit"}>Send!</button>
      </form>
    </>
  );
}

export default App;

import { useEffect, useState, useRef } from "react";
import "./App.css";
import Paho from "paho-mqtt";

function App() {
  const [img, setImg] = useState("");
  const [topic, setTopic] = useState("all");
  const [msg, setMsg] = useState("");
  const clientRef = useRef(null);
  const input = useRef(null);

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
      useSSL: true,
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
    if (msg === "" && img === "") return;
    if (clientRef.current && clientRef.current.isConnected()) {
        const message = new Paho.Message(
            JSON.stringify({
                msg: msg,
                img: img,
            })
        );
        message.destinationName = "70656e6973/" + topic;
        clientRef.current.send(message);
        setMsg("");
        setImg("");
        input.current.value = "";
    }
  };

  const handleFileChange = (event) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const uploadedFile = files[0];
      const reader = new FileReader();

      reader.onload = async (event) => {
        const fileData = event.target.result.toString();
        setImg(fileData);
      };
      reader.readAsDataURL(uploadedFile);
    }
  };

  return (
    <>
      <div className={"start"}/>
      <div className={"bg"}>
        <form onSubmit={sendMessage} className="sendForm">
          <select onChange={(e) => setTopic(e.target.value)}>
            <option value={"all"}>All</option>
            <option value={"chris"}>Chris</option>
            <option value={"simon"}>Simon</option>
            <option value={"akira"}>Akira</option>
          </select>
          <textarea
            onChange={(event) => setMsg(event.target.value)}
            ref={input}
            type=""
          />
          <label for="file-upload" className="custom-file-upload">
            Upload img
          </label>
          <input type="file" id="file-upload" onChange={handleFileChange} />
          <button id="send" type={"submit"}>
            Send!
          </button>
        </form>
      </div>
    </>
  );
}

export default App;

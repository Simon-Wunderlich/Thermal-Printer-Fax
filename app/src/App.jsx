import { useEffect, useState, useRef } from "react";
import { DateFormatter } from "@internationalized/date"
import "./App.css";
import Paho from "paho-mqtt";

const formatter = new DateFormatter("en-GB", {
  weekday: "short",
  day: "numeric",
  month: "short",
  hour: "numeric",
  minute: "numeric",
  hour12: true
})


function App() {
  const storedName = localStorage.getItem("name") || ""

  const [_name, set_Name] = useState(storedName);
  const [name, setName] = useState(storedName);
  const [img, setImg] = useState("");
  const [topic, setTopic] = useState("all");
  const [msg, setMsg] = useState("");
  const clientRef = useRef(null);
  const input = useRef(null);
  const [justSubmitted, setJustSubmitted] = useState(false);
  const [receivedConfirmationPrint, setReceivedConfirmationPrint] = useState(false)
  const [receivedConfirmationQueue, setReceivedConfirmationQueue] = useState(false)
  const [receivedFailure, setReceivedFailure] = useState(false)
  const [receivedResponse,  setReceivedResponse] = useState(false);


  useEffect(() => {
    const video = document.getElementsByClassName('start')[0];

    // Wait for video details to load before jumping to the timestamp
    video.addEventListener('loadedmetadata', function() {
      console.log(video.currentTime)
      video.currentTime = 0; // Jump to 0 seconds
      video.play()
    });

    video.addEventListener('timeupdate', function handleLoop() {
      if (video.currentTime >= 4) {
        const videoCont = document.getElementsByClassName('videoCont')[0];
        if (!videoCont)
          return
        videoCont.remove()
      }
    })


    // 1. Initialize the Client
    const client = new Paho.Client(
      "broker.hivemq.com", // Replace with your MQTT broker address
      8884,
      crypto.randomUUID(),
    );


    function showReturn(which)
    {
      console.log("showing the return");
      if (which.type=="p")
      {
        console.log("it printed!");
        setReceivedConfirmationPrint(true);
        setTimeout(() => { setReceivedConfirmationPrint(false) }, 2000);
      }
      else
      {
        setReceivedConfirmationQueue(true);
        setTimeout(() => { setReceivedConfirmationQueue(false) }, 2000);
      }
    }

    function on_message(message)
    {
      setReceivedResponse(true);
      console.log("Recieved Return from Printer");
      const data = JSON.parse(message.payloadString);
      console.log(data);
      console.log(data.topic);
      console.log(data.type);
      showReturn(data);
    }

    client.onMessageArrived = on_message;

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
        client.subscribe("70656e6973/acknowledge")
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
          header: name + " at " + formatter.format(new Date()),
        }),
      );
      message.destinationName = "70656e6973/" + topic;
      clientRef.current.send(message);
      showSubmission();
      setMsg("");
      setImg("");
      input.current.value = "";
      setTimeout(() => {
        if (receivedResponse && !(receivedConfirmationPrint||receivedConfirmationQueue)) {
          setReceivedResponse(false);
        }
        else {
          setReceivedFailure(true);
          setReceivedResponse(false);
          setTimeout(() => { setReceivedFailure(false) }, 2000);
        }
      }, 10000);
    }
  };
  function showSubmission() {
    console.log("Sent. Confirmation light enabling");
    setJustSubmitted(true);
    // setTimeout(, 20000);
    setTimeout(() => {
      setJustSubmitted(false);
    }, 2000);
  }

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

  function storeName(e) {
    e.preventDefault();
    setName(_name)
    if (_name)
      localStorage.setItem("name", _name)
  }

  return (
    <div style={{height:"100vh", overflow:"clip", position:"relative"}}>
      <div className={"videoCont"}>
        <video muted autoPlay className={"start"}>
          <source src={window.innerWidth > 1000 ? "/FaxBoot.mov" : "/FaxBoot_mobile.mov"} type="video/quicktime"/>
        </video>
      </div>
        { !name ?
            <div className={"bg-blank"}>
              <form onSubmit={(e) => storeName(e)} className="sendForm">
                <div className={"nameInput"}>
                  <p>Enter your name</p>
                  <input onInput={(e) => set_Name(e.target.value)}/>
                  <button style={{width: "40px", height: "30px"}}>Ok</button>
                </div>
              </form>
            </div>
         :
            <div className={"bg"}>

            <form onSubmit={sendMessage} className="sendForm">
          <select onChange={(e) => setTopic(e.target.value)}>
            <option value={"all"}>All</option>
            <option value={"chris"}>Chris</option>
            <option value={"simon"}>Simon</option>
            <option value={"lachie"}>Lachie</option>
            <option value={"akira"}>Akira</option>
          </select>
          <textarea
            onChange={(event) => setMsg(event.target.value)}
            ref={input}
            type=""
          />
          <label htmlFor="file-upload" className="custom-file-upload">
            Upload img
          </label>
          <input type="file" id="file-upload" onChange={handleFileChange} />
          <button id="send" type={"submit"}>
            Send!
          </button>
        </form>

          {justSubmitted ? <div className="conf_light" id="submit_conf"></div> : <></>}
          {receivedConfirmationPrint ? <div className="conf_light"  id="print_conf"></div> : <></>}
          {receivedConfirmationQueue ? <div className="conf_light" id="queue_conf"></div> : <></>}
          {receivedFailure ? <div className="conf_light" id="fail_conf"></div> : <></>}
      </div>
        }
    </div>
  );
}

export default App;

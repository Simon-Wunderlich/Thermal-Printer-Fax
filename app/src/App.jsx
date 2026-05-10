import {useEffect, useState} from 'react'
import './App.css'

function App() {
  const [msg, setMsg] = useState("")
  const [socket, setSocket] = useState(null)

  useEffect(() => {
    // connect to ws
    const _socket = new WebSocket('ws://test.sorry.horse:8765')
    setSocket(_socket)
  }, []);

  const sendMessage = () => {
    socket.send(msg)
    socket.close()
  }

  return (
    <>
      <form onSubmit={sendMessage}>
        <input onChange={event => setMsg(event.target.value)}/>
        <p>{msg}</p>
        <button type={"submit"}>Send!</button>
      </form>
    </>
  )
}

export default App

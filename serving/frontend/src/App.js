/* eslint-disable */
// import "antd/dist/antd.css";
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Message, NavBar } from './components';
import { UploadVideo, SelectPerson, SelectVideo, SelectVideoTmp } from './pages';


function App() {
  return (
    <div className="App">
      {/* NavBar, Message는 어디에다가 둬야 하지? */}
      <BrowserRouter>
        <NavBar />
        {/*<Message />*/}
        <Routes>
          <Route path="/" element={<UploadVideo />} />
          <Route path="/select-person" element={<SelectPerson />} />
          <Route path="/select-video" element={<SelectVideo />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;

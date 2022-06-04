/* eslint-disable */
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { NavBar } from './components';
import { UploadVideo, SelectPerson, SelectVideo } from './pages';


function App() {
  return (
    <div className="App" style={{paddingTop: "50px"}}>
      <BrowserRouter>
        <NavBar />
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

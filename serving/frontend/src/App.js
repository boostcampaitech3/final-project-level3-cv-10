/* eslint-disable */
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Header, Footer } from './components';
import { UploadVideo, SelectPerson, SelectVideo } from './pages';
import { LaughterContext } from './context';
import React, { useState, useEffect } from 'react';


function App() {

  const [laughterTimeline, setLaughterTimeline] = useState();
  const value = { laughterTimeline, setLaughterTimeline };

  useEffect(() => {
    if (laughterTimeline) {
      console.log(laughterTimeline);
    }
    
  }, [laughterTimeline]);

  return (
    <div className="App" 
        style={{paddingTop: "50px", display: "flex", flexDirection: "column", minHeight: "100vh"}}>
      <BrowserRouter>
        <Header />
        <LaughterContext.Provider value={value}>
        <Routes>
          <Route path="/" element={<UploadVideo />} />
          <Route path="/select-person" element={<SelectPerson />} />
          <Route path="/select-video" element={<SelectVideo />} />
        </Routes>
        </LaughterContext.Provider>
        <Footer />
      </BrowserRouter>
    </div>
  );
}

export default App;

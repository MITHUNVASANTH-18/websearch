import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PromptPage from "./Components/PromptPage";
import ImageVideoPage from "./Components/ImageVideoPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<PromptPage />} />
        <Route path='/images-videos' element={<ImageVideoPage />} />
      </Routes>
    </Router>
  );
}

export default App;

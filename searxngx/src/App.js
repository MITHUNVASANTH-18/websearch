import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PromptPage from "./Components/PromptPage";
import ImageVideoPage from "./Components/ImageVideoPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<ImageVideoPage />} />
        <Route path='/prompt' element={<PromptPage />} />
      </Routes>
    </Router>
  );
}

export default App;

import React from "react";
import "./App.css";

import Features from "./components/Features";
import Unlock from "./components/Unlock";
import Plans from "./components/Plans";
import Hero from "./components/Hero";
import Mission from "./components/Mission";
import Freetrial from "./components/Freetrial";
import Footer from "./components/Footer";
import Testimonial from "./components/Testimonial";

function App() {
  return (
    <div className="w-full min-h-screen font-sans bg-white">
      <Hero />

      <Features />
      <Unlock />
      <Plans />
      <Mission />
      <Testimonial />
      <Freetrial />
      <Footer />
    </div>
  );
}

export default App;

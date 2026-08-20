import { useState } from "react";
import Nav from "./components/Nav";
import Hero from "./components/Hero";
import Pipeline from "./components/Pipeline";
import Dashboard from "./components/Dashboard";
import Evaluation from "./components/Evaluation";
import Footer from "./components/Footer";

export default function App() {
  const [active, setActive] = useState("home");

  return (
    <div className="min-h-screen bg-base text-slate-200">
      <Nav active={active} setActive={setActive} />
      <Hero setActive={setActive} />
      <Pipeline />
      <Dashboard />
      <Evaluation />
      <Footer />
      </div>
  );
}
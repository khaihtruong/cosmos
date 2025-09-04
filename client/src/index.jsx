import * as ReactDOMClient from "react-dom/client";
import Login from "./components/Login.jsx";
import NavBar from  "./components/NavBar.jsx";
import Chat from "./components/Chat.jsx";
import React from "react";
import {BrowserRouter, Routes, Route} from "react-router-dom";
import "./index.css"

const container = document.getElementById("root");
const root = ReactDOMClient.createRoot(container);

root.render(
  <BrowserRouter>
    <Routes>
      <Route path = "/" element = {<Login />}/>
      <Route path = "/navbar" element = {<NavBar />}/>
      <Route path = "/chat" element = {<Chat />}/>
    </Routes>
  </BrowserRouter>
)
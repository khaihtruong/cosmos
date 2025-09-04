import { NavLink } from "react-router-dom";
import "../style/NavBar.css"

export default function NavBar() {
  return (
    <div className = 'NavBar_container'>
      <nav>
        <ul className = "Menu_list">
          <li><NavLink to = "/dashboard">Dashboard</NavLink></li>
          <li><NavLink to = "/datareport">Chat</NavLink></li>
          <li><NavLink to = "/document">Documentation</NavLink></li>
          
        </ul>
      </nav>
    </div>
  )
  
}
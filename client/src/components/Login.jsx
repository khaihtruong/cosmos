import { useState } from "react";
import "../style/Login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("User");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Email:", email);
    console.log("Password:", password);
    console.log("Role:", role);
  };

  return (
    <div className="login_container">
      <form onSubmit={handleSubmit} className="login-form">
        <h1>Cosmo</h1>

        {/* Role Toggle */}
        <div className="toggle-container">
          {["User", "Provider"].map((option) => (
            <label
              key={option}
              className={`toggle-option ${role === option ? "active" : ""}`}
            >
              <input
                type="radio"
                name="role"
                value={option}
                checked={role === option}
                onChange={() => setRole(option)}
              />
              {option}
            </label>
          ))}
        </div>

        <input 
          type="email"
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />
        <br />
        <input 
          type="password"
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        <br />
        <input type="submit" value="Login" />
      </form>
    </div>
  );
}

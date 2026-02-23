import express from "express";

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

/**
 * In-memory store
 * {
 *   username: [ { plot, owner, brainrots: [] } ]
 * }
 */
const DATA = {};

/* Roblox posts data */
app.post("/update", (req, res) => {
  const { user, plots } = req.body;
  if (!user || !plots) {
    return res.status(400).json({ error: "bad payload" });
  }

  DATA[user] = plots;
  console.log("UPDATE FROM", user);
  res.json({ ok: true });
});

/* Worker gets all active users */
app.get("/users", (req, res) => {
  res.json(Object.keys(DATA));
});

/* Worker gets one user */
app.get("/users/:user", (req, res) => {
  res.json(DATA[req.params.user] || []);
});

app.listen(PORT, () => {
  console.log("API running on", PORT);
});

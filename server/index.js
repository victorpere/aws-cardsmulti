const express = require("express");
const app = express();
const port = 5000;

app.get("/helloworld", (req, res) => {
  res.send({ message: "Hello, World!" });
});

app.listen(port, () => {
  console.log("express listening on port " + port);
});

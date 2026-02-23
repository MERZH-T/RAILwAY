const express = require("express");
const fs = require("fs");
const { xorEncrypt, xorDecrypt } = require("./crypto");

const app = express();
app.use(express.text({ limit: "10mb" }));
app.use(express.json());

const CLIENT_KEY = process.env.CLIENT_KEY || "gurt_client_key_777";
const ADMIN_KEY  = process.env.ADMIN_KEY  || "i-need-to-make-this-long-otherwise-its-not-secure-popcorn12";

let store = fs.existsSync("store.json")
  ? JSON.parse(fs.readFileSync("store.json", "utf8"))
  : {};

function save() {
  fs.writeFileSync("store.json", JSON.stringify(store, null, 2));
}

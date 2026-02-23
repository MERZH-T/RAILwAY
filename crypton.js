const XOR_KEY = process.env.XOR_KEY || "gurtblud";

function xorDecrypt(base64) {
  const data = Buffer.from(base64, "base64");
  const out = Buffer.alloc(data.length);

  for (let i = 0; i < data.length; i++) {
    out[i] = data[i] ^ XOR_KEY.charCodeAt(i % XOR_KEY.length);
  }
  return out.toString("utf8");
}

function xorEncrypt(str) {
  const buf = Buffer.from(str, "utf8");
  const out = Buffer.alloc(buf.length);

  for (let i = 0; i < buf.length; i++) {
    out[i] = buf[i] ^ XOR_KEY.charCodeAt(i % XOR_KEY.length);
  }
  return out.toString("base64");
}

module.exports = { xorEncrypt, xorDecrypt };

const express = require("express");
const bodyParser = require("body-parser");
var cors = require("cors");
const { spawn, exec } = require("child_process");
const fs = require("fs");

const app = express();

app.use(bodyParser.urlencoded({ extended: false }));
app.use(cors()); // Use this after the variable declaration
app.use(express.json());

app.post("/scrapy", async (req, res, next) => {
  console.log("Received post request at backend's /scrapy: ", req.body);

  let param1;
  let param2;
  let param3;
  let ms;
  try {
    let temp = req.body.time;
    // console.log("temp type", typeof temp, " and is ", temp); //for error testing

    if (!temp || isNaN(temp)) {
      console.log("Forcing ms to be 2000");
      temp = 2;
    }
    ms = temp * 1000;
    param1 = req.body.allowedDomains[0];
    param2 = req.body.startUrls[0];
  } catch (err) {
    return;
  }

  console.log("Process will run for (ms) ", ms);
  if (!param1 || param1.trim() === "") {
    console.log(
      "allowedDomains input (param1) is empty, setting to buyandsell.gc.ca"
    );
    param1 = "buyandsell.gc.ca";
  }
  if (!param2 || param2.trim() === "") {
    console.log(
      "startUrls input (param2) is empty, setting to https://buyandsell.gc.ca/for-businesses"
    );

    param2 = "https://buyandsell.gc.ca/for-businesses";
  }
  if (
    !req.body.deny ||
    !Array.isArray(req.body.deny) ||
    (Array.isArray(req.body.deny) &&
      req.body.deny.length === 1 &&
      req.body.deny[0].trim() === "")
  ) {
    param3 = [];
    console.log("param3 is empty: ", param3);
  } else {
    param3 = req.body.deny;
    console.log("param3 is", param3);
  }
  let to_add_string = ``;

  if (param3.length > 0) {
    for (let i = 0; i < param3.length; ++i) {
      to_add_string += `-a arg${i}=${param3[i]} `;
    }
  }
  to_add_string = to_add_string.trim();

  let success = true;

  const cmd = exec(
    //sample param1 domains=buyandsell.gc.ca
    //sample param2 start=https://buyandsell.gc.ca/for-businesses
    `scrapy crawl keybas -a domains=${param1} -a start=${param2} ${to_add_string}`,
    (error, stdout, stderr) => {
      if (error) {
        console.log(
          "An error occured within scrapy. Gracefully handling and not closing server"
        );
        error = new Error(`Scrapy raised an error: ${error}`);

        success = false;
        res.status(error.code || 424);
        res.json({ message: error.message || "An unknown error occurred!" });
        return;
      }
    }
  );

  await setTimeout(
    () => {
      cmd.kill();
      console.log(
        `Scrapy crawl's time is up. Scrapy crawl process has been killed`
      );
      if (!success) {
        return;
      }
      const filePath = "./scrapy_output.csv";
      try {
        fs.exists(filePath, function (exists) {
          //https://stackoverflow.com/questions/10046039/node-js-send-file-in-response
          if (exists) {
            res.writeHead(200, {
              "Content-Type": "application/octet-stream",
              "Content-Disposition":
                "attachment; filename=" + "scrapy_output.csv",
            });
            fs.createReadStream(filePath).pipe(res);
            return;
          }
          res.writeHead(400, { "Content-Type": "text/plain" });
          res.end("ERROR File does not exist");
        });
      } catch (err) {}
    },
    ms ? ms : 2000
  );
});

app.listen(5000, () => console.log("server listening on port 5000"));

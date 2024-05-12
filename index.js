/* eslint-disable no-var */
/* eslint-disable max-len */

const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp(functions.config().firebase);

// admin.initializeApp({
//  credential: admin.credential.cert(require("./serviceAccountKey.json")), // Replace with your file path
//  databaseURL: "https://<your-project-id>.firebaseio.com", // Replace with your project ID
// });

var database = admin.database();

// func triggered per change in any rect_data:
exports.sendNotificationToTopic = functions.database.ref("/rooms/{roomId}/{cam_num}/rect_data").onWrite(async (change, context) => {
  var oldRectData = change.before.val();
  var newRectData = change.after.val();
  var camId = context.params.cam_num;
  var roomId = context.params.roomId; // Capture roomId

  database.ref("metadata/msgSent/").set("Camera " + camId + " changed its rect data" + oldRectData + " to " + newRectData);

  // get polygon data: // into format [[x,y],[x,y]...]
  var masksPath = `/rooms/${roomId}/${camId}_mask`;
  const masksRef = database.ref(masksPath);
  const snapshot = await masksRef.once("value");
  var polygonsValues = [];

  // Create a new sub-array for each polygon
  snapshot.forEach((childSnapshot) => {
    var polygon = [];
    // Split the string by underscores
    const parts = childSnapshot.val().split("_");

    // Loop through pairs of coordinates and add them to the polygon
    for (let i = 0; i < parts.length; i += 2) {
      const x = parseInt(parts[i]);
      const y = parseInt(parts[i + 1]);
      polygon.push([x, y]);
    }
    polygonsValues.push(polygon);
  });

  database.ref("metadata/debugPoint/").set(0);
  database.ref("metadata/pathCheck/masksPath/").set("masksPath is: " + masksPath);
  database.ref("metadata/maskValues/").set("maskValues[0] is: " + polygonsValues[0] + " maskValues is [1]: " + polygonsValues[1]);

  // todo validate: [[[,],[,]],[[,],[,]]] of polygonsValues

  var rectPath = `/rooms/${roomId}/${camId}/rect_data`;
  const rectRef = database.ref(rectPath);
  const rectData = await rectRef.once("value");
  const parts = rectData.val().split("_");

  database.ref("metadata/pathCheck/rectPath/").set("rectPath is: " + rectPath);
  database.ref("metadata/rectData/").set("rectData is: " + rectData.val());

  // Check if the first number is 0 (do nothing)
  if (parseInt(parts[0]) == 0) {
    return null;
  }
  database.ref("metadata/debugPoint/").set(1);

  // Calculate the number of average points (excluding format at the end)
  const numPoints = parseInt(parts[0]);

  // Initialize arrays for X and Y averages
  const avgXYPeopleLoc = [];

  // avg of _ x y x y as first people location, etc for more ppls
  for (let i = 1; i < numPoints * 4; i += 4) { // Loop increments by 4
    const startX1 = parseInt(parts[i]); // First X for point 1
    const startY1 = parseInt(parts[i + 1]); // First Y for point 1
    const startX2 = parseInt(parts[i + 2]); // Second X for point 1
    const startY2 = parseInt(parts[i + 3]); // Second Y for point 1

    // check horizontal state (not standing):
    if (Math.abs(startX2 - startX1) < Math.abs(startY2 - startY1)) {
      continue;
    }

    const avgX1 = (startX1 + startX2) / 2; // Average X for point 1
    const avgY1 = (startY1 + startY2) / 2; // Average Y for point 1

    avgXYPeopleLoc.push([avgX1, avgY1]);
  }
  if (avgXYPeopleLoc.length == 0) {
    database.ref("metadata/debugPoint/").set(1.5);
    return null;
  }

  database.ref("metadata/debugPoint/").set(2);

  // calc if within polygon:
  var classifyPoint = require("robust-point-in-polygon");

  var counter = 0;
  var problematicState = false;
  var isOuside = true;
  avgXYPeopleLoc.forEach((peopleLoc) => { // [[x1, y1], [x2,y2]...]
    isOuside = true;
    polygonsValues.forEach((definedPolygon) => { // [[[poligonA_x1, poligonA_y1],[,]]...],[[poligonB_x1, poligonB_y1],[x2, y2]]]
      if ((classifyPoint(definedPolygon, peopleLoc)) != 1) { // 1 means outside
        isOuside = false;
      } else { // outside current polygon:
        counter = counter + 1;
      }
    });
    if ((isOuside == true) && (problematicState == false)) {
      database.ref("metadata/polygonRes/").set(peopleLoc + " outside of polygon ");
      database.ref("metadata/polygon/").set("avg loc is :" + peopleLoc + " outside of " + polygonsValues);
      counter = counter - 1000;
      problematicState = true;
      return;
    }
  });
  database.ref("metadata/counter/").set(counter);
  database.ref("metadata/debugPoint/").set(2.5);
  if (problematicState == false) {
    counter = counter + 100;
    database.ref("metadata/polygonRes/").set("within a polygon ");
    database.ref("metadata/polygon/").set(avgXYPeopleLoc + " is inside of " + polygonsValues);
    database.ref("metadata/counter/").set(counter);
  } else {
    counter = counter + 100000;
    database.ref("metadata/counter/").set(counter);

    // FCM msging:
    try {
      // getting tokens & sending to them:
      var tokenLstPath = `/rooms/${roomId}/token_lst`;
      const tokensRef = database.ref(tokenLstPath);

      database.ref("metadata/debugPointToken/").set(-2);

      const snapshot = await tokensRef.once("value");
      const tokenList = snapshot.val() || {}; // Handle empty list
      database.ref("metadata/debugPointToken/").set(-1);
      for (const key in tokenList) {
        if (Object.keys(tokenList).length > 0) {
          database.ref("metadata/debugPointToken/").set(0);
          // Loop through child nodes (tokens)
          const token = tokenList[key];
          const tokenMessage = {
            notification: {
                  title: ("Someone might have fallen at " + roomId), //roomId - place_name
              body: ("Check camera: " + camId + ". It has changed its identification area from " + oldRectData + " to " + newRectData + "."),
            },
            token: token,
          };
          try {
            const response = await admin.messaging().send(tokenMessage);
            database.ref("metadata/debugPointToken/").set(1);
            database.ref("metadata/debugPointTokenKey/").set(key);
            // Optional: Log response details for debugging (avoid full token)
            const responseWithoutToken = {...response, token: "[REDACTED]"};
            database.ref(`metadata/fcmtokenrespoLog/${response.messageId}`).set(String(response) + " " + responseWithoutToken);
          } catch (error) {
            // todo
          }
        }
      }

      // Optional: Write additional details about the sent message to a temporary log in Realtime Database
      // database.ref("metadata/fcmLog/").set({message: message, response: response});

      database.ref("metadata/debugPoint/").set(5);
    } catch (error) {
      console.error("Error sending FCM message:", error);

      // Add more detailed logging based on error.code (if available)
      const errorCode = error.code || "Unknown error";
      database.ref("metadata/fcmError/").set({code: errorCode, message: error.message});
      database.ref("metadata/debugPoint/").set(4);
    }
  }
});

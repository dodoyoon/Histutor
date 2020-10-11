onmessage = ({ data }) => {
  const [tuteePk, req_type, ws_url] = data ;
  const websocket = new WebSocket(ws_url);
  websocket.onmessage = ({ data }) => {
    const { type, next_tutee_pk, next_tutee_url } = JSON.parse(data);
    if(type === req_type && next_tutee_pk === tuteePk){
      send_notification("학우님의 차례가 되었습니다.");
      postMessage(next_tutee_url);
    }
  }
}

const send_notification = (message) => {
  try{
    if (Notification.permission === "granted") {
      const notification = new Notification(message,);
    }
    else if (Notification.permission !== "granted") {
      Notification.requestPermission().then(function (permission) {
        if (permission === "granted") {
          const notification = new Notification(message);
        }
      });
    }
  }catch(err){
    alert("This browser does not support desktop notification");
  }

}
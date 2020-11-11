(function(){
  const perm_status = Notification.permission;
  const $notification_status = document.getElementById("notification_container");
  const alarm_announcement_url = `https://www.notion.so/20-09-21-9c716eb8d8224b7499a1fcf7e272865a`;
  if(perm_status === 'granted'){
    $notification_status.innerHTML = `
    <div class='noti-success'>
      <div class='noti__title'> 📥 알림이 설정되었습니다 </div>
      <div class='noti__helptext'>튜터링이 시작되면 알림을 받으실 수 있습니다.</div>
    </div>
    `;
  }else{
    $notification_status.innerHTML =  `
    <div class='noti-warning'>
     <div class='noti__title'>🚨 알림 설정이 필요합니다 🚨</div>
     <div class='noti__helptext'>튜터링이 시작되어도 알림을 받지 못하며, 화면이 안 옮겨질 수 있습니다.</div>
     <div class='noti__link'><a href=${alarm_announcement_url} target="_blank">🔗알림 설정 바로가기</a></div>
    </div>`
    ;
  }
})();

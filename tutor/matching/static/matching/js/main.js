(function(){
  const colorMainTab = () => {
    let pathname = window.location.pathname ;
    const pathnameArr = pathname.split('/') ;
    const selected = pathnameArr[pathnameArr.length-2] ; 
    const mainTabArr = document.querySelectorAll('button.mybutton.main_tab') ;
    mainTabArr.forEach(tab => {
      if(tab.value === selected){
        tab.style.background = 'rgb(212 207 231)' ;
      }
    }) 
  }
  colorMainTab() ;
})() ;

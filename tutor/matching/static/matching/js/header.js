(function(){
  const languageButton = document.querySelector('button.language') ; 
  languageButton.addEventListener('click', (e) => {
    console.dir(e);
    const selectLanguageBox = document.querySelector('div.language') ; 
    selectLanguageBox.classList.toggle('hidden') ; 
  })
})();
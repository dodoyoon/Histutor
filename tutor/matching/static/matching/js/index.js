import * as header from './header.js' ; 

(function(){
  const languageButton = document.querySelector('button.language') ; 
  
  languageButton.addEventListener('click', header.languageHandler) ; 
  document.body.addEventListener('click', header.closeLanguageHandler) ; 
})();
const selectLanguageBox = document.querySelector('div.language') ; 
export const languageHandler = (e) => {
  selectLanguageBox.classList.toggle('hidden') ; 
}
export const closeLanguageHandler = (e) => {
  if(e.target.className === 'language' || e.target.closest('.language')) return ; 
  if(!selectLanguageBox.classList.contains('hidden'))
    selectLanguageBox.classList.add('hidden') ;
}

"use strict";

function copyToClipboard(text, successMessage, manualCopyMessage = null) {
  return navigator.clipboard.writeText(text).then(
    function() {
      showFadeOutMessage(successMessage);
    },
    function() {
      if (manualCopyMessage) {
        /* Если скопировать не удалось, показываем диалог со ссылкой. */
        window.prompt(manualCopyMessage, text);
      }
    }
  );
}

function copyImageToClipboard($img) {
  let src = $img.attr('src');
  let getImagePromise = async () => {
    let data = await fetch(src);
    return await data.blob();
  }

  return navigator.clipboard.write([
    new ClipboardItem({
      'image/png': getImagePromise()
    })
  ]).catch(function(e) {
    console.error(e);
    throw e;
  });
}

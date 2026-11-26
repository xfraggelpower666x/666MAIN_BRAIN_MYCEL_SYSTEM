const source=new URLSearchParams(location.search).get('source')==='originals'?'originals':'imports';
const image=document.querySelector('#boot-image');
image.addEventListener('error',()=>{image.hidden=true;},{once:true});
image.src='../'+source+'/boot/666_UNIVERSAL_PYTHON_ELECTRON_BUILDKIT_R01/electron/renderer/assets/bootscreen-1920x1080.webp';
window.cc.onBoot(s=>{document.querySelector('#boot-status').textContent=s});

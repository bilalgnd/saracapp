constcolors=["#F44336","#9C27B0","#2196F3","#4CAF50","#FFC107","#FF9800","#795548","#FFFFFF"];
constingredients_list=["Soğan","Domates","Patates","Ketçap","Mayonez","Turşu"];
constfree_extras_list=["SadeEt","Soslu","Gemi","Kayık"];
constpayment_list=["POS","NAKİT","Paket","Dükkaniçi"];

letcurrentColor=localStorage.getItem('waiterColor')||"";
letmenuData={et:[],tavuk:[],kampanya:[],icecekler:[],ekstralar:{}};
letactiveTables=[];
letdraft_items=[];
letactive_table_name=null;
letis_order_screen_open=false;
letws=null;

//Elements
consttopAppBar=document.getElementById('topAppBar');
constappTitle=document.getElementById('appTitle');
constkasaStatus=document.getElementById('kasaStatus');
constbackBtn=document.getElementById('backBtn');
consttabRow=document.getElementById('tabRow');
constmenuArea=document.getElementById('menuArea');
constmasalarArea=document.getElementById('masalarArea');
constmasalarList=document.getElementById('masalarList');
constfabMasalar=document.getElementById('fabMasalar');
constbottomAppBar=document.getElementById('bottomAppBar');
constbabTitle=document.getElementById('babTitle');
constbabSubtitle=document.getElementById('babSubtitle');
constproductSheet=document.getElementById('productSheet');
constsheetOverlay=document.getElementById('sheetOverlay');

letcurrentProduct=null;
letcurrentQty=1;
letcurrentOption=null;
letcurrentDrinks={};

//Stateforchips
letselected_notes={};
letselected_additions={};
letselected_paid_extras={};
letselected_free_extras={};
letselected_payments={};

functionenableDragScroll(slider){
if(!slider)return;
letisDown=false;
letstartY;
letscrollTop;

slider.addEventListener('mousedown',(e)=>{
isDown=true;
startY=e.pageY-slider.offsetTop;
scrollTop=slider.scrollTop;
});
slider.addEventListener('mouseleave',()=>{isDown=false;});
slider.addEventListener('mouseup',()=>{isDown=false;});
slider.addEventListener('mousemove',(e)=>{
if(!isDown)return;
e.preventDefault();
consty=e.pageY-slider.offsetTop;
constwalk=(y-startY)*1.5;
slider.scrollTop=scrollTop-walk;
});
}

functioninit(){
initColorSettings();
fetchMenu();
connectWebSocket();

enableDragScroll(menuArea);
enableDragScroll(masalarList);
enableDragScroll(productSheet);

document.querySelectorAll('.tab-btn').forEach(btn=>{
btn.addEventListener('click',(e)=>{
consttarget=e.currentTarget;
document.querySelector('.tab-btn.active').classList.remove('active');
target.classList.add('active');
renderMenu(target.dataset.tab);
});
});

fabMasalar.onclick=()=>open_tables_screen();
backBtn.onclick=()=>close_tables_screen();
document.getElementById('babCancel').onclick=cancelActiveOrder;
document.getElementById('babSend').onclick=sendOrder;

document.getElementById('qtyMinus').onclick=()=>{if(currentQty>1){currentQty--;updateSheetPrice();}};
document.getElementById('qtyPlus').onclick=()=>{currentQty++;updateSheetPrice();};
sheetOverlay.onclick=closeProductSheet;
document.getElementById('addToCartBtn').onclick=addProductToDraft;
}

functioninitColorSettings(){
constgrid=document.getElementById('colorGrid');
colors.forEach(c=>{
constcircle=document.createElement('div');
circle.className='color-circle'+(c===currentColor?'selected':'');
circle.style.background=c;
circle.onclick=()=>{
document.querySelectorAll('.color-circle').forEach(el=>el.classList.remove('selected'));
circle.classList.add('selected');
currentColor=c;
localStorage.setItem('waiterColor',c);
};
grid.appendChild(circle);
});

document.getElementById('settingsBtn').onclick=()=>{
document.getElementById('settingsModal').classList.add('open');
document.getElementById('settingsOverlay').classList.add('open');
};
document.getElementById('closeSettingsBtn').onclick=()=>{
document.getElementById('settingsModal').classList.remove('open');
document.getElementById('settingsOverlay').classList.remove('open');
};
}

asyncfunctionfetchMenu(){
try{
constres=awaitfetch('/menu');
constdata=awaitres.json();

menuData={
et:data.meat||[],
tavuk:data.chicken||[],
kampanya:data.campaign||[],
icecekler:data.drinks||[],
ekstralar:data.extras||{}
};
renderMenu('et');
}catch(e){
console.error("Menufetcherror",e);
}
}

functionconnectWebSocket(){
ws=newWebSocket('ws://'+location.host+'/ws');
ws.onopen=()=>{
kasaStatus.innerText="🟢KasaBağlı";
kasaStatus.classList.add('online');
setInterval(()=>{if(ws.readyState===WebSocket.OPEN)ws.send("ping");},2000);
};
ws.onmessage=(e)=>{
activeTables=JSON.parse(e.data);
fabMasalar.innerText=`Masalar(${activeTables.length})`;
if(is_order_screen_open)render_tables_list();
};
ws.onclose=()=>{kasaStatus.innerText="🔴KasaÇevrimdışı";kasaStatus.classList.remove('online');setTimeout(connectWebSocket,3000);};
ws.onerror=()=>ws.close();
}

functiongetCardColorClass(name){
name=name.toLowerCase();
if(name.includes("etporsiyon")||name.includes("beyti")||name.includes("iskender"))return"dark-red";
if(name.includes("hatayusulu"))return"cream";
if(name.includes("bigadoner"))return"blue";
if(name.includes("tavukporsiyon")||name.includes("pilavustu"))return"dark-orange";
if(name.includes("tombik"))return"orange";
if(name.includes("eskiusul"))return"red";
if(name.includes("durum"))return"yellow";
return"";
}

functiongetDrinkColorClass(name){
name=name.toLowerCase();
if(name.includes("cocacola")||name.includes("şişekola")||name.includes("kutukola")||name.includes("colazero"))return"cola-red";
if(name.includes("sprite"))return"sprite-green";
if(name.includes("fanta"))return"fanta-yellow";
if(name.includes("ayran"))return"ayran-white";
if(name.includes("su")&&!name.includes("şalgam"))return"water-blue";
if(name.includes("soda"))return"soda-green";
if(name.includes("şalgam"))return"salgam-purple";
return"";
}

functionrenderMenu(tab){
menuArea.innerHTML='';
constitems=menuData[tab]||[];
items.forEach(item=>{
constcard=document.createElement('div');
card.className='card'+getCardColorClass(item.name);
card.innerHTML=`
<divclass="card-title">${item.name}</div>
<divclass="card-price">${item.options[0].price}₺</div>
`;
card.onclick=()=>openProductSheet(item,tab==='icecekler');
menuArea.appendChild(card);
});
}

functionrenderChipGroup(containerId,items,stateObj,isNegative,colorClass,onUpdate){
constcontainer=document.getElementById(containerId);
container.innerHTML='';
items.forEach(item=>{
letlabel=typeofitem==='string'?item:item.label;
letkey=typeofitem==='string'?item:item.key;
if(isNegative){
letn=label;
label=n+"sız";
if(n==="Soğan")label="Soğansız";
if(n==="Domates")label="Domatessiz";
if(n==="Patates")label="Patatessiz";
if(n==="Ketçap")label="Ketçapsız";
if(n==="Mayonez")label="Mayonezsiz";
if(n==="Turşu")label="Turşusuz";
}elseif(containerId==='icerikEkleContainer'){
letn=label;
label=n+"lı";
if(n==="Soğan")label="Soğanlı";
if(n==="Domates")label="Domatesli";
if(n==="Patates")label="Patatesli";
if(n==="Ketçap")label="Ketçaplı";
if(n==="Mayonez")label="Mayonezli";
if(n==="Turşu")label="Turşulu";
}

constchip=document.createElement('div');
chip.className='chip'+colorClass;
chip.innerText=label;
chip.onclick=()=>{
stateObj[key]=!stateObj[key];
if(stateObj[key])chip.classList.add('selected');
elsechip.classList.remove('selected');

//MutuallyexclusivelogicforicerikCikarandicerikEkle
if(containerId==='icerikCikarContainer'&&stateObj[key]){
if(selected_additions[key]){
selected_additions[key]=false;
renderChipGroup('icerikEkleContainer',ingredients_list,selected_additions,false,'chip-yellow');
}
}elseif(containerId==='icerikEkleContainer'&&stateObj[key]){
if(selected_notes[key]){
selected_notes[key]=false;
renderChipGroup('icerikCikarContainer',ingredients_list,selected_notes,true,'chip-red');
}
}

if(onUpdate)onUpdate();
};
container.appendChild(chip);
});
}

functionopenProductSheet(item,isDrink){
currentProduct=item;
currentQty=1;
currentOption=item.options[0];
currentDrinks={};
selected_notes={};
selected_paid_extras={};
selected_free_extras={};
selected_payments={};

document.getElementById('sheetProductName').innerText=item.name;
document.getElementById('qtyText').innerText=currentQty;

constoptsContainer=document.getElementById('optionsContainer');
optsContainer.innerHTML='';
item.options.forEach(sec=>{
constchip=document.createElement('div');
chip.className='chip'+(sec===currentOption?'selected':'');
letgramajAdi=sec.portion||sec.portion;
chip.innerText=gramajAdi==='Standart'?`${sec.price}₺`:`${gramajAdi}(${sec.price}₺)`;
chip.onclick=()=>{
currentOption=sec;
Array.from(optsContainer.children).forEach(c=>c.classList.remove('selected'));
chip.classList.add('selected');
updateSheetPrice();
};
optsContainer.appendChild(chip);
});

consticerikCikarSec=document.getElementById('icerikCikarSection');
constdrinksSec=document.getElementById('drinksSection');

if(!isDrink){
icerikCikarSec.classList.remove('hidden');
renderChipGroup('icerikCikarContainer',ingredients_list,selected_notes,true,'chip-red');
selected_additions={};
renderChipGroup('icerikEkleContainer',ingredients_list,selected_additions,false,'chip-yellow');

constucretliArr=Object.keys(menuData.extras||{}).map(k=>({key:k,label:`${k}(+${menuData.extras[k]}₺)`}));
renderChipGroup('ucretliEkstralarContainer',ucretliArr,selected_paid_extras,false,'chip-yellow',updateSheetPrice);

renderChipGroup('ucretsizEkstralarContainer',free_extras_list,selected_free_extras,false,'chip-dark');
renderChipGroup('odemeContainer',payment_list,selected_payments,false,'chip-dark');

if(menuData['icecekler']&&menuData['icecekler'].length>0){
drinksSec.classList.remove('hidden');
constdCont=document.getElementById('drinksContainer');
dCont.innerHTML='';
menuData['icecekler'].forEach(ic=>{
constdBtn=document.createElement('button');
dBtn.className='drink-btn'+getDrinkColorClass(ic.name);
dBtn.innerText=ic.name;
dBtn.onclick=()=>{
currentDrinks[ic.name]=(currentDrinks[ic.name]||0)+1;
renderDrinksList(dCont);
updateSheetPrice();
};
dCont.appendChild(dBtn);
});
}else{
drinksSec.classList.add('hidden');
}
}else{
icerikCikarSec.classList.add('hidden');
drinksSec.classList.add('hidden');
}

document.getElementById('noteInput').value='';

constmasaSec=document.getElementById('masaAdiSection');
if(active_table_name){
masaSec.classList.add('hidden');
}else{
masaSec.classList.remove('hidden');
document.getElementById('masaInput').value='';
}

updateSheetPrice();
productSheet.classList.add('open');
sheetOverlay.classList.add('open');
}

functionrenderDrinksList(container){
Array.from(container.children).forEach(btn=>{
constname=btn.innerText.replace(/[0-9]/g,'').trim();
constcount=currentDrinks[name]||0;
if(count>0){
btn.classList.add('selected');
btn.innerHTML=`${name}<divclass="drink-badge">${count}</div>`;
}else{
btn.classList.remove('selected');
btn.innerText=name;
}
});
}

functionupdateSheetPrice(){
letucretliFiyat=0;
Object.keys(selected_paid_extras).forEach(k=>{
if(selected_paid_extras[k])ucretliFiyat+=(menuData.extras[k]||0);
});

letbasePrice=(currentOption.price+ucretliFiyat)*currentQty;
letdrinkPrice=0;

if(menuData['icecekler']){
menuData['icecekler'].forEach(ic=>{
if(currentDrinks[ic.name]){
drinkPrice+=(currentDrinks[ic.name]*ic.options[0].price);
}
});
}

consttotal=basePrice+drinkPrice;
document.getElementById('addToCartBtn').innerText=`SiparişeEkle(${total}₺)`;
}

functioncloseProductSheet(){
productSheet.classList.remove('open');
sheetOverlay.classList.remove('open');
}

functionaddProductToDraft(){
constsiparisNotu=document.getElementById('noteInput').value.trim();
lettableInput=document.getElementById('masaInput').value.trim();

if(!active_table_name){
if(!tableInput)tableInput="YeniSipariş";
active_table_name=tableInput;
enterActiveTableMode();
}

consttumNotlar=[];
Object.keys(selected_notes).forEach(k=>{
if(selected_notes[k]){
letlabel=k+"sız";
if(k==="Soğan")label="Soğansız";
if(k==="Domates")label="Domatessiz";
if(k==="Patates")label="Patatessiz";
if(k==="Ketçap")label="Ketçapsız";
if(k==="Mayonez")label="Mayonezsiz";
if(k==="Turşu")label="Turşusuz";
tumNotlar.push(label);
}
});
Object.keys(selected_additions).forEach(k=>{
if(selected_additions[k]){
letlabel=k+"lı";
if(k==="Soğan")label="Soğanlı";
if(k==="Domates")label="Domatesli";
if(k==="Patates")label="Patatesli";
if(k==="Ketçap")label="Ketçaplı";
if(k==="Mayonez")label="Mayonezli";
if(k==="Turşu")label="Turşulu";
tumNotlar.push(label);
}
});
Object.keys(selected_free_extras).forEach(k=>{if(selected_free_extras[k])tumNotlar.push(k);});
Object.keys(selected_paid_extras).forEach(k=>{if(selected_paid_extras[k])tumNotlar.push(k);});
Object.keys(selected_payments).forEach(k=>{if(selected_payments[k])tumNotlar.push(k);});
if(siparisNotu)tumNotlar.push(siparisNotu);

constbirlesikNot=tumNotlar.join(",");

letucretliFiyat=0;
Object.keys(selected_paid_extras).forEach(k=>{
if(selected_paid_extras[k])ucretliFiyat+=(menuData.extras[k]||0);
});

letanlikBirimFiyat=currentOption.price+ucretliFiyat;
letgramajAdi=currentOption.portion||currentOption.portion;

for(leti=0;i<currentQty;i++){
draft_items.push({
name:currentProduct.name,
portion:gramajAdi,
price:anlikBirimFiyat,
notes:birlesikNot
});
}

if(menuData['icecekler']){
menuData['icecekler'].forEach(ic=>{
if(currentDrinks[ic.name]){
leticGramaj=ic.options[0].portion||ic.options[0].portion;
for(leti=0;i<currentDrinks[ic.name];i++){
draft_items.push({
name:ic.name,
portion:icGramaj,
price:ic.options[0].price,
notes:""
});
}
}
});
}

updateBottomAppBar();
closeProductSheet();
}

functionenterActiveTableMode(){
topAppBar.classList.add('active-mode');
appTitle.innerText=`${active_table_name}İlave`;
fabMasalar.classList.add('hidden');
bottomAppBar.classList.remove('hidden');
}

functioncancelActiveOrder(){
active_table_name=null;
draft_items=[];
topAppBar.classList.remove('active-mode');
appTitle.innerText="SARAÇOĞLUDÖNER";
fabMasalar.classList.remove('hidden');
bottomAppBar.classList.add('hidden');
}

functionupdateBottomAppBar(){
babTitle.innerText=`Masa:${active_table_name}`;
consttotal=draft_items.reduce((sum,i)=>sum+i.price,0);
babSubtitle.innerText=`${draft_items.length}Ürün-${total}₺`;
}

functionopen_tables_screen(){
is_order_screen_open=true;
appTitle.innerText="AçıkMasalar";
kasaStatus.classList.add('hidden');
document.getElementById('settingsBtn').classList.add('hidden');
backBtn.classList.remove('hidden');
tabRow.classList.add('hidden');
menuArea.classList.add('hidden');
fabMasalar.classList.add('hidden');
masalarArea.classList.remove('hidden');
render_tables_list();
}

functionclose_tables_screen(){
is_order_screen_open=false;
appTitle.innerText="SARAÇOĞLUDÖNER";
kasaStatus.classList.remove('hidden');
document.getElementById('settingsBtn').classList.remove('hidden');
backBtn.classList.add('hidden');
tabRow.classList.remove('hidden');
menuArea.classList.remove('hidden');
if(!active_table_name)fabMasalar.classList.remove('hidden');
masalarArea.classList.add('hidden');
}

window.deleteItem=function(customer_name,index){
if(!confirm('Buürünüsilmekistediğinizeeminmisiniz?'))return;
consttable=activeTables.find(t=>t.customer_name===customer_name);
if(!table)return;
table.items.splice(index,1);

if(table.items.length===0){
fetch('/close_bill',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_name:customer_name})});
}else{
consttotal=table.items.reduce((sum,i)=>sum+i.price,0);

constdata={customer_name:customer_name,items:table.items,total_amount:total,color:table.color};
fetch('/siparis',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
}
};

window.editNote=function(customer_name,index){
consttable=activeTables.find(t=>t.customer_name===customer_name);
if(!table)return;
constcurrentNote=table.items[index].notes||"";
constnewNote=prompt("Yeninotugirin:",currentNote);
if(newNote!==null){
table.items[index].notes=newNote.trim();
consttotal=table.items.reduce((sum,i)=>sum+i.price,0);

constdata={customer_name:customer_name,items:table.items,total_amount:total,color:table.color};
fetch('/siparis',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
}
};

window.togglePrepared=function(customer_name,current_status){
constnew_status=current_status==='prepared'?'waiting':'prepared';
fetch('/update_status',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({customer_name:customer_name,status:new_status})
});
};

functionrender_tables_list(){
masalarList.innerHTML='';
activeTables.forEach(t=>{
constcard=document.createElement('div');
card.className='adisyon-card';
letitemsHtml=(t.items||[]).map((k,index)=>`
<divstyle="border-bottom:1pxsolid#444;padding:10px0;">
<divclass="a-item"style="display:flex;justify-content:space-between;align-items:center;">
<divclass="a-item-name"style="flex:1;">1x${k.name}${k.portion!=='Standart'?`(${k.portion})`:''}</div>
<divstyle="display:flex;align-items:center;gap:8px;">
<divclass="a-item-price"style="margin-right:8px;">${k.price}₺</div>
<buttonclass="btn-icon-small"onclick="editNote('${t.customer_name}',${index})">✏️</button>
<buttonclass="btn-icon-small"onclick="deleteItem('${t.customer_name}',${index})"style="color:var(--danger);">🗑️</button>
</div>
</div>
${k.notes?`<divstyle="font-size:12px;color:#aaa;margin-top:4px;">*${k.notes}</div>`:''}
</div>
`).join('');

letcolorIndicator=t.color?`<divstyle="width:16px;height:16px;border-radius:50%;background-color:${t.color};margin-right:8px;display:inline-block;vertical-align:middle;"></div>`:'';
lettitlePrefix=t.status==='prepared'?'<spanstyle="color:#4CAF50;font-weight:bold;margin-right:8px;">✔</span>':'';

card.innerHTML=`
<divclass="adisyon-header"style="display:flex;align-items:center;justify-content:space-between;">
<divclass="adisyon-title"style="display:flex;align-items:center;">
${colorIndicator}
${titlePrefix}${t.customer_name}${t.is_updated?'<spanstyle="font-size:0.6em;color:#FF9800;margin-left:5px;">(Eklendi)</span>':''}
</div>
<divclass="adisyon-time">${t.time||''}</div>
</div>
<divclass="adisyon-items">${itemsHtml}</div>
<divclass="adisyon-footer"style="flex-direction:column;gap:12px;margin-top:8px;">
<divstyle="display:flex;justify-content:space-between;width:100%;">
<divclass="adisyon-total"style="font-size:24px;">TOPLAM:${t.total_amount}₺</div>
</div>
<divstyle="display:grid;grid-template-columns:1fr1fr;gap:8px;width:100%;">
<buttonclass="btn-ilave"style="background:#2196F3;">➕İlave</button>
<buttonclass="btn-yazdir"style="background:#424242;">🖨️FişYazdır</button>
<buttonclass="btn-tamam"style="background:#4CAF50;grid-column:span2;">💳Ödendi/Kapat</button>
</div>
</div>
`;

letpressTimer;
letisPressed=false;
letpStartY=0;

conststartPress=(e)=>{
if(e.target.closest('button'))return;
isPressed=true;
pStartY=e.pageY||(e.touches&&e.touches[0].pageY)||0;
pressTimer=setTimeout(()=>{
if(isPressed){
isPressed=false;
if(navigator.vibrate)navigator.vibrate(50);
window.togglePrepared(t.customer_name,t.status);
}
},500);
};

constcancelPress=()=>{
isPressed=false;
clearTimeout(pressTimer);
};

constmovePress=(e)=>{
if(!isPressed)return;
letcurrentY=e.pageY||(e.touches&&e.touches[0].pageY)||0;
if(Math.abs(currentY-pStartY)>10){
cancelPress();
}
};

card.addEventListener('mousedown',startPress);
card.addEventListener('touchstart',startPress,{passive:true});
card.addEventListener('mousemove',movePress);
card.addEventListener('touchmove',movePress,{passive:true});
card.addEventListener('mouseup',cancelPress);
card.addEventListener('mouseleave',cancelPress);
card.addEventListener('touchend',cancelPress);
card.addEventListener('touchcancel',cancelPress);

card.querySelector('.btn-ilave').onclick=()=>{
active_table_name=t.customer_name;
//MapbacktoTurkishkeysfordraft_itemssothe"SipariseEkle"screenworks
draft_items=[...(t.items||[])];
close_tables_screen();
enterActiveTableMode();
updateBottomAppBar();
};
card.querySelector('.btn-tamam').onclick=()=>{
fetch('/close_bill',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_name:t.customer_name})});
};
card.querySelector('.btn-yazdir').onclick=()=>{
fetch('/yazdir',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_name:t.customer_name})});
};
masalarList.appendChild(card);
});
}

asyncfunctionsendOrder(){
if(draft_items.length===0)return;
consttotal=draft_items.reduce((sum,i)=>sum+i.price,0);
constm_adi=active_table_name;

//Maptoenglishkeysforserver


constdata={
customer_name:m_adi==="YeniSipariş"?"":m_adi,
items:draft_items,
total_amount:total,
color:currentColor
};
try{
constreq=awaitfetch('/siparis',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify(data)
});
if(req.ok)cancelActiveOrder();
elsealert("Gönderilemedi!Kasauygulamasındahataolabilir.");
}catch(e){
alert("Kasabağlantıhatası!");
}
}

init();

const c1 = document.getElementById("currency-one");
const c2 = document.getElementById("currency-two");
const c3 = document.getElementById("currency-three");
const amount1 = document.getElementById("amount-one");
const amount2 = document.getElementById("amount-two");

// myHeaders.append("apikey", "o0K8l61XHvgWeVO2T2eg4bLre2bTysMh"); //laaufey
var myHeaders = new Headers();
myHeaders.append("apikey", "PtCaN8XaWyHbv3BNijh9yNAvNC3izl8Y"); //laufeycat

var requestOptions = {
  method: 'GET',
  redirect: 'follow',
  headers: myHeaders
};

const curr1 = c1.value;

const api_isk_dkk = `https://api.apilayer.com/exchangerates_data/convert?to=DKK&from=ISK&amount=${curr1}`
const api_isk_eur = `https://api.apilayer.com/exchangerates_data/convert?to=EUR&from=ISK&amount=${curr1}`
async function calculater(){
  const dkk = await fetch(`https://api.apilayer.com/exchangerates_data/convert?to=DKK&from=ISK&amount=${curr1}`, requestOptions)
  const eur = await fetch(`https://api.apilayer.com/exchangerates_data/convert?to=EUR&from=ISK&amount=${curr1}`, requestOptions)
  var dkk_data = await dkk.json();
  var eur_data = await eur.json();
  const dk_result = dkk_data.result;
  const dk_rounded = dk_result.toFixed(2);
  const eur_result = eur_data.result;
  const eur_rounded = eur_result.toFixed(2);
  c2.value = dk_rounded;
  c3.value = eur_rounded;
}
calculater();


async function calculate(from, amount){
  const dkk = await fetch(`https://api.apilayer.com/exchangerates_data/convert?to=DKK&from=${from}&amount=${amount}`, requestOptions)
  const eur = await fetch(`https://api.apilayer.com/exchangerates_data/convert?to=EUR&from=${from}&amount=${amount}`, requestOptions)
  const isk = await fetch(`https://api.apilayer.com/exchangerates_data/convert?to=ISK&from=${from}&amount=${amount}`, requestOptions)
  var dkk_data = await dkk.json();
  var eur_data = await eur.json();
  var isk_data = await isk.json();
  const dk_result = dkk_data.result;
  const dk_rounded = dk_result.toFixed(2);
  const eur_result = eur_data.result;
  const eur_rounded = eur_result.toFixed(2);
  const isk_result = isk_data.result;
  const isk_rounded = isk_result.toFixed(2);
  c1.value = isk_rounded;
  c2.value = dk_rounded;
  c3.value = eur_rounded;
}

document.getElementById("account").addEventListener("click", showHide);
function showHide(account_id){
  console.log(document.querySelector(`[id='${account_id}']`))
  console.log("Show Hide")
  const table = document.querySelector(`[id='account-table-${account_id}']`)
  console.log(document.querySelector(`[id='account-table-${account_id}']`))
  table.classList.toggle("hidden")
}

// fetch(`https://api.apilayer.com/exchangerates_data/convert?to=DKK&from=ISK&amount=${curr1}`, requestOptions)
//   .then(response => response.json())
//   .then(result => console.log(result))
//   .catch(error => console.log('error', error));
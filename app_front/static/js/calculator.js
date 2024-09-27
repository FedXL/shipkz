
    var MyData;
    let description3,result3,taxes,RealResult3;
    const MyCalculator = document.getElementById("MyCalculator");
    const MyResult = document.getElementById("MyResult");

    const UsdEurChanger = () => {
        let value = document.getElementById('currency').value;
        let PrefixElements = document.getElementsByClassName('currency-prefix');
        let SuffixElements = document.getElementsByClassName('currency-suffix');

        if (value == 'USD') {
            for (let i = 0; i < PrefixElements.length; i++) {
                PrefixElements[i].textContent = '$';
            }
            for (let i = 0; i < SuffixElements.length; i++) {
                SuffixElements[i].textContent = 'USD';
            }
        }
        else if (value == 'EUR') {
            for (let i = 0; i < PrefixElements.length; i++) {
                PrefixElements[i].textContent = '€';
            }
            for (let i = 0; i < SuffixElements.length; i++) {
                SuffixElements[i].textContent = 'EUR';
            }
        }
    }

    const CalculateCommission = (orderData, price, delivery) => {



        let price_rub = parseFloat(price);
        let delivery_rub = parseFloat(delivery);
        let total = price_rub + delivery_rub;
        let usd = orderData.usd;
        let eur = orderData.eur;
        let curcur = orderData.CurrencyType;
        if (curcur === "USD"){

            if (total >= usd * 499) {
                return 0.25;
            }else{
                return 0.3;
            }
        }
        else if (curcur ==='EUR') {

            if (total >= eur * 499) {
                return 0.25;
            } else {
                return 0.3;
            }

        }

    }

    const calculateVolumeWeight = () => {

        let height = document.getElementById("height").value;
        let length = document.getElementById("length").value;
        let width = document.getElementById("width").value;

        let resultField = document.getElementById("sizeLabelNumber");
        let result = (height * length * width)/5000;
        result = Math.round(result * 100) / 100;
        resultField.textContent  = result + "кг";
    }


     function handleData() {
        MyData = ExchangeRates;
        console.log('incoming data');
        console.log(MyData);
    }

    function createItemElement(mainText,descriptionText,itemValue) {

        const resultItem = document.createElement("div");
        const paragraphContainer = document.createElement("div");
        const firstParagraph = document.createElement("p");

        const secondParagraph = document.createElement("p");
        const valueDiv = document.createElement("div");

        resultItem.className = "result-item";
        firstParagraph.className = "result-item-name";
        secondParagraph.className = "result-item-description";

        paragraphContainer.appendChild(firstParagraph);
        paragraphContainer.appendChild(secondParagraph);

        firstParagraph.textContent = mainText;
        secondParagraph.textContent = descriptionText;

        valueDiv.textContent = itemValue;
        valueDiv.className = "result-item-value";

        resultItem.appendChild(paragraphContainer);
        resultItem.appendChild(valueDiv);

        return resultItem;
    }



    function calculateCost(weight) {
        const priceRanges = {
            '1-2': 900,
            '3': 1100,
            '4': 1300,
            '5': 1500,
            '6': 1800,
            '7': 2000,
            '8': 2200,
            '9': 2400,
            '10': 2700,
            '11': 2900,
            '12-14': 3100,
            '15-30': 3300,
            '31-40': 4400,
            '41-50': 5500,
            '51-60': 6600
        };
    let roundedWeight = Math.round(weight);

    if (weight < 1 && weight > 0) {
        return 900;
    }

    for (let range in priceRanges) {
        let [min, max] = range.split('-').map(Number);
        max = max || min;
        if (roundedWeight >= min && roundedWeight <= max) {
            return priceRanges[range];
        }
    }

    return "Спец тариф";
}
    handleData();
    UsdEurChanger();

    document.addEventListener('DOMContentLoaded', function() {
        const button = document.getElementById('calculate');
        const buttonAgain = document.getElementById('TryAgain');

        if (button) {
            button.addEventListener('click', function() {

                const currency = document.getElementById('currency').value;
                const priceInCurrency = document.getElementById('order-value').value;
                const weight = document.getElementById('order-weight').value;

                const currencyInfo = () => {
                    let MyInfo = {
                        TypeCurrency : currency,
                        RealCurrency : null,
                        FraudCurrency : null,
                        FraudDate : null,
                    }

                    if (currency === 'USD') {
                        MyInfo.RealCurrency = MyData.usd.price;
                        MyInfo.FraudCurrency = MyData.sber_usd.price;
                        MyInfo.FraudDate = MyData.sber_usd.data;
                        MyInfo.Coefficient = MyData.usd.price/MyData.eur.price;
                        MyInfo.usd = MyData.usd.price;
                        MyInfo.eur = MyData.eur.price;
                        MyInfo.CurrencyType = 'USD';

                    }

                    else if (currency === 'EUR'){
                        MyInfo.RealCurrency = MyData.eur.price;
                        MyInfo.FraudCurrency = MyData.sber_euro.price;
                        MyInfo.FraudDate = MyData.sber_euro.data;
                        MyInfo.usd = MyData.usd.price;
                        MyInfo.eur = MyData.eur.price;
                        MyInfo.CurrencyType = "EUR";
                    }
                    return MyInfo;
                }
                const OrderInfo = currencyInfo(MyData);

                OrderInfo.CountryChoice = MyData.CountryChoice;
                OrderInfo.DeliveryChoice = MyData.DeliveryChoice;

                OrderInfo.RealPriceInRub = Math.round(OrderInfo.RealCurrency * priceInCurrency);
                OrderInfo.FraudPriceInRub = Math.round(OrderInfo.FraudCurrency * priceInCurrency);

                OrderInfo.InsuranceCDEK = Math.round(OrderInfo.FraudPriceInRub * 0.005);

                OrderInfo.CDEK = calculateCost(weight);




                const result = document.getElementById("resultContainer");
                let description  = `${OrderInfo.FraudDate} 1 ${OrderInfo.TypeCurrency} = ${OrderInfo.FraudCurrency} RUB`;
                let result1 = `${OrderInfo.FraudCurrency} ₽`;
                const CurrencyItem = createItemElement("Курс на покупку в Сбербанк",description, result1);
                const firstParagraph = CurrencyItem.querySelector(".result-item-name");

// Создаём элемент ссылки
                const linkElement = document.createElement("a");
                linkElement.href = "http://www.sberbank.ru/ru/quotes/currencies?tab=kurs&currency=USD&currency=EUR&package=ERNP-2";
                linkElement.textContent = "Курс на покупку в Сбербанк";
                linkElement.target = "_blank"; // Открыть ссылку в новой вкладке
                linkElement.classList.add("mark-main-color");

                // Очищаем параграф и добавляем ссылку внутрь него
                firstParagraph.textContent = '';  // Очистка текста параграфа
                firstParagraph.appendChild(linkElement);

                let description2 = `${priceInCurrency} ${currency} Х ${OrderInfo.FraudCurrency} ₽`;
                let result2 = `${OrderInfo.FraudPriceInRub} ₽`;
                const PriceItem = createItemElement("Стоимость заказа",description2,result2);

                if (OrderInfo.CountryChoice === 'usa') {
                    let getVolumeWeight = document.getElementById('sizeLabelNumber');
                    let VolumeWeight = getVolumeWeight.textContent.replace(/кг/g, '').trim();
                    let VolumeWeightNumber = parseFloat(VolumeWeight);

                    if (weight >= VolumeWeightNumber){
                        description3 = `${weight} X 16 X ${MyData.sber_usd.price} USD`;
                        result3 = `${Math.round(weight*16*MyData.sber_usd.price)} ₽`;
                        RealResult3 = weight*16*MyData.usd.price;
                        OrderInfo.CDEK = calculateCost(weight);
                    }else{
                        description3 = `${VolumeWeightNumber} X 16 X ${MyData.sber_usd.price} USD`;
                        result3 = `${Math.round(VolumeWeightNumber*16*MyData.sber_usd.price)} ₽`;
                        RealResult3 = VolumeWeightNumber*16*MyData.usd.price;
                        OrderInfo.CDEK = calculateCost(VolumeWeightNumber);
                    }

                } else if (OrderInfo.CountryChoice === 'europe') {
                    let deliveryFixedPrice = document.getElementById('deliveryCost').value;

                    if (deliveryFixedPrice) {
                        description3 = `Стоимость доставки ${deliveryFixedPrice} ${currency} X ${OrderInfo.FraudCurrency} ₽`;
                        result3 = `${Math.round(OrderInfo.FraudCurrency * deliveryFixedPrice)} ₽`;
                        RealResult3 = OrderInfo.RealCurrency * deliveryFixedPrice;
                    } else {
                        alert('Надо заполнить поле стоимости доставки');
                        return;
                    }

                } else {
                    alert('Надо выбрать регион');
                    return;
                }

                const DeliveryToKzItem = createItemElement("Стоимость доставки в Казахстан",description3,result3);

                let description4 = `Усредненное значение ${OrderInfo.CDEK} ₽ + страхование 0.5% ${OrderInfo.InsuranceCDEK} ₽`;
                let result4 = `${OrderInfo.CDEK + OrderInfo.InsuranceCDEK} ₽`;
                const CDEKitem = createItemElement("Доставка СДЕК из Казахстана в Россию",description4, result4);
                let description5 = `Расходы на перевод денег, конвертацию, таможенное сопровождение и пересылку.`;

                let commissionKOF = CalculateCommission(OrderInfo, OrderInfo.RealPriceInRub, RealResult3);

                result.appendChild(CurrencyItem);
                result.appendChild(PriceItem);
                result.appendChild(DeliveryToKzItem);
                result.appendChild(CDEKitem);

                let description6;
                let result6;
                if (currency === 'EUR' && priceInCurrency > 200) {
                    taxes = (priceInCurrency - 200) * 0.15;
                    description6 = `Сумма облагаемая сбором ${priceInCurrency - 200} ${currency} в 15%`
                    result6 = `${Math.round(taxes * OrderInfo.FraudCurrency)} ₽`;
                } else if (currency === 'USD' && priceInCurrency * OrderInfo.Coefficient > 200) {

                    taxes = (priceInCurrency * OrderInfo.Coefficient - 200) * 0.15;
                    taxes = Math.round(taxes);
                    description6 = `Сумма облагаемая сбором ${Math.round(priceInCurrency - 200 / OrderInfo.Coefficient)} ${currency} в 15%`
                    result6 = `${Math.round(taxes * OrderInfo.FraudCurrency)} ₽`;
                }
                let CommissionCalculate;
                if (taxes) {

                    const Taxes = createItemElement("Таможенный сбор свыше 200 евро", description6, result6);
                    result.appendChild(Taxes);

                    CommissionCalculate = (OrderInfo.RealPriceInRub + RealResult3) * (commissionKOF+1) + (taxes * OrderInfo.RealCurrency)*1.05 - (parseFloat(result3) + OrderInfo.FraudPriceInRub + taxes * OrderInfo.FraudCurrency);


                    CommissionCalculate = Math.round(CommissionCalculate);
                }else {

                    CommissionCalculate = (OrderInfo.RealPriceInRub + RealResult3) * (commissionKOF+1) - (parseFloat(result3) + OrderInfo.FraudPriceInRub);
                    CommissionCalculate = Math.round(CommissionCalculate);
                }

                const Castoms = createItemElement('Услуги таможенного брокера ', "Примерная сумма","1000 ₽" );

                result.appendChild(Castoms);

                const result5 = `${CommissionCalculate} ₽`;
                const Commission = createItemElement("Наша комиссия", description5, result5);
                result.appendChild(Commission);
                let resultValues = document.querySelectorAll('.result-item-value');
                let totalSum = 0;

                for (let i = 1; i < resultValues.length; i++) {
                    let value = parseFloat(resultValues[i].textContent);

                    if (!isNaN(value)) {
                        totalSum += value;
                    }
                }
                totalSum = Math.round(totalSum);
                totalSum = `${totalSum} ₽`;

                let descriptionTotal;
                if (OrderInfo.CountryChoice === 'usa') {
                    let totalUperMegaSumm = (commissionKOF+1) * OrderInfo.RealPriceInRub;
                    totalUperMegaSumm = Math.round(totalUperMegaSumm);
                    descriptionTotal = `Выкуп до склада форвардера  ${totalUperMegaSumm} ₽ `
                } else {
                    descriptionTotal = "Примерная сумма к оплате"
                }

                const TotalResult = createItemElement("Итого",descriptionTotal, totalSum);
                result.appendChild(TotalResult);
                taxes = null;
                MyCalculator.style.display='none';
                MyResult.style.display='block';
            });
        }
        if (buttonAgain) {
            buttonAgain.addEventListener('click',function() {
                let resultContainer = document.getElementById('resultContainer');
                let divElements = resultContainer.getElementsByTagName('div');
                for (let i = divElements.length - 1; i >= 0; i--) {
                    let divElement = divElements[i];
                    divElement.parentNode.removeChild(divElement);
                }
                MyCalculator.style.display='block';
                MyResult.style.display='none';
            });
        }
        const usa = document.getElementById('usa');
        const europe = document.getElementById('europe');
        const deliverySection = document.getElementById('DeliverySection');
        const WeightContainer  = document.getElementById('weightContainer');
        usa.addEventListener('click', function() {
            let EuropeDeliveryContainer = document.getElementById('DeliveryChoice');
            EuropeDeliveryContainer.style.display = "none";
            let UsaBulkWeigh = document.getElementById('sizeContainer');
            UsaBulkWeigh.style.display = "block";
            MyData.CountryChoice = "usa";
            deliverySection.style.display = 'block';
            WeightContainer.style.display = 'flex';
        });
        europe.addEventListener('click', function() {
            let EuropeDeliveryContainer = document.getElementById('DeliveryChoice');
            EuropeDeliveryContainer.style.display = "none";
            let UsaBulkWeigh = document.getElementById('sizeContainer');
            UsaBulkWeigh.style.display = "block";
            MyData.CountryChoice = "usa";
            deliverySection.style.display = 'block';
            WeightContainer.style.display = 'flex';
        });
        let heightInput = document.getElementById("height");
        let lengthInput = document.getElementById("length");
        let widthInput = document.getElementById("width");
        heightInput.addEventListener("change", calculateVolumeWeight);
        lengthInput.addEventListener("change", calculateVolumeWeight);
        widthInput.addEventListener("change", calculateVolumeWeight);

        ExchangeChanger = document.getElementById('currency');
        ExchangeChanger.addEventListener('change',UsdEurChanger);

        let CreateOrder = document.getElementById('MakeOrder');
        CreateOrder.addEventListener('click', function(){
                window.location.href = 'https://shipkz.ru/request-form/';
            }
        )
    });


console.log('START FULLY MESSANGER');
const new_user = exportUser;

function autoExpand(element) {
        element.style.height = 'auto';
        element.style.height = (element.scrollHeight) + 'px';}

document.addEventListener("DOMContentLoaded", function() {
        let clearButtoN = document.getElementById('buttonSendText');
        clearButtoN.disabled = true;
        var messageWindow = document.getElementById('messageWindow');
        const options = {
            threshold: 0.8
        };
        const observerPhoto = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const containerWithPhoto = entry.target;
                    let file = containerWithPhoto.filePath;
                    let target = containerWithPhoto.id;
                    if (!containerWithPhoto.classList.contains('loaded')) {
                        sendAskForFile(target, file, ws);
                        containerWithPhoto.classList.add('loaded');
                    }
                }
            });
        }, options);

        const observerIsRead = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const containerContainer = entry.target;
                    let target = containerContainer.id;
                    if (!containerContainer.classList.contains('read')) {
                        sendIReadThisMessage(target,ws);
                        console.log(`pew pew is read target ${target}`);
                        containerContainer.classList.add('read');
                    }
                }
            });
        }, options);

const createErrorCloud = () => {
        const containerDiv = document.createElement('div');
        containerDiv.className = 'oneMessageContainer';
        const messageDiv = document.createElement('div');
        messageDiv.className = 'oneMessageText';
        const sendTime = document.createElement('div');
        sendTime.className = 'timeElement';
        const spacerDiv = document.createElement('div');
        spacerDiv.className = 'spacer';

        messageDiv.textContent = "Соединение с сервером разорвано. Пожалуйста обновите страницу.";
        messageDiv.style.backgroundColor = '#d22e2e';
        messageDiv.style.color = 'black';
        messageDiv.appendChild(sendTime);
        containerDiv.appendChild(messageDiv);
        containerDiv.appendChild(spacerDiv);
        return containerDiv;
}

const gapCheckerForClouds = (is_answer, manager)=>{
    let report = { separateClass: "",
        details: "create_manager_string"
    }

    let transleter = {true:'yes', false:'no'};
    let yesOrNo = transleter[is_answer];

    let myElemets = document.getElementById('messageWindow');
    let lastElement = myElemets.lastElementChild;

    if (lastElement === null) {
        report.separateClass = "oneMessageGap";
        if (is_answer===true) {
            report.details = manager;
            return report;
        } else {
            report.details = null;
            return report;
        }
    }
    if (yesOrNo === lastElement.getAttribute('is_answer')) {
        report.separateClass = "oneMessageLaminar";
        report.details = null;
    } else{
        report.separateClass = "oneMessageGap";
    }
    if (yesOrNo === "yes" && yesOrNo !== lastElement.getAttribute('is_answer')) {
        report.details = manager;
        report.separateClass = "oneMessageLaminar";
    } else {
        report.details = null;
    }
    return report;
}

const createTextCloud = (data) => {
    is_answer = data.is_answer;
    text = data.text;
    manager = data.user_name;
    time = data.time;
    message_id = data.message_id;
    is_read = data.is_read

    const containerDiv = document.createElement('div');
    containerDiv.className = 'oneMessageContainer';

    if (is_read===true) {
        containerDiv.classList.add('read');
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'oneMessageText';
    messageDiv.textContent = text;
    const sendTime = document.createElement('div');
    sendTime.className = 'timeElement';
    if (is_answer === true) {
        sendTime.textContent = time;
        containerDiv.setAttribute('is_answer', 'yes');
    } else {
        sendTime.textContent = time;
        containerDiv.setAttribute('is_answer', 'no');
    }

    const spacerDiv = document.createElement('div');
    spacerDiv.className = 'spacer';
    if (is_answer === true) {
        messageDiv.appendChild(sendTime);
        messageDiv.style.backgroundColor = '#EDEDED';
        messageDiv.style.color = 'black';
        containerDiv.appendChild(messageDiv);
        containerDiv.appendChild(spacerDiv);
    } else {
        messageDiv.appendChild(sendTime);
        containerDiv.appendChild(spacerDiv);
        containerDiv.appendChild(messageDiv);
    }
    containerDiv.id = "messageCloud"+message_id;
    return containerDiv;
};

const createManagerCloud = (manager) => {
    const containerDiv = document.createElement('div');
    containerDiv.className = 'oneMessageContainer';
    containerDiv.classList.add("oneMessageGap");
    const messageDiv = document.createElement('div');
    messageDiv.className = 'managerContainer';
    messageDiv.textContent = manager
    const spacerDiv = document.createElement('div');
    spacerDiv.className = 'spacer';
    messageDiv.style.color = '#888888';
    containerDiv.appendChild(messageDiv);
    containerDiv.appendChild(spacerDiv);
    return containerDiv;
}

function createImageFromBase64(base64Data, mimi) {
    const img = document.createElement('img');
    img.src = `data:${mimi};base64,${base64Data}`;
    return img;
}

function base64ToFile(base64Data, mime) {
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new File([byteArray], 'document', { type: mime });
}

function downloadFile(file, fileName) {
    console.log('start download file');
    const url = URL.createObjectURL(file);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.style.display = 'none';

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

const sendAskForFile = (target, path, ws) => {
console.log(`ASK for file ${target}`);
    let data = {
        event: "downloadStatic",
        targetID: target,
        path: path
    };
    ws.send(JSON.stringify(data));
};
const sendIReadThisMessage = (target, ws) => {
    const datetime = new Date();
    console.log(`Send notification about user have read this ${target} at ${datetime}`);
    let data = {
        event: "isReadMessage",
        targetID: target,
        time: datetime.toISOString(),
    };
    ws.send(JSON.stringify(data));
}

const createOrderCloud = (Data) => {

    let text = Data.text;
    let messageID = Data.message_id
    let time = Data.time;




    const containerDiv = document.createElement('div');
    containerDiv.className = 'oneMessageContainer';
    containerDiv.id = "messageCloud" + messageID;
    const messageDiv = document.createElement('div');
    messageDiv.className = 'oneMessageText';
    const sendTime = document.createElement('div');
    sendTime.className = 'timeElement';
    const spacerDiv = document.createElement('div');
    spacerDiv.className = 'spacer';

    let parts = text.split('_');
    let number = parts[1];

    messageDiv.textContent = "Мы получили вашу заявку. Заказ №: " + String(number) + "." + " Ожидайте ответа менеджера.";
    messageDiv.style.backgroundColor = '#fec502';
    messageDiv.style.color = 'black';
    sendTime.textContent = time;
    messageDiv.appendChild(sendTime);
    containerDiv.appendChild(messageDiv);
    containerDiv.appendChild(spacerDiv);
    return containerDiv;
}

function cleanManager(manager) {
    if (manager == null) {
        return null;
    }
    if (manager.includes('[') || manager.includes(']')) {
        const cleanedManager = manager.replace(/[\[\]]/g, '');
        return cleanedManager;
    }
    return manager;
}


const appendMessageCloud = (messageData, ws=null) => {
    let newCloud,anotherCloud,managerClean;
    managerClean = cleanManager(messageData.user_name);
    messageData.user_name = managerClean;
    let spacer_report =gapCheckerForClouds(messageData.is_answer, managerClean);

    if (messageData.message_type === 'text') {
        newCloud = createTextCloud(messageData);
    }
    else if (messageData.message_type ==='order') {
        // newCloud = createTextCloud(messageData)
        // newCloud.style.backgroundColor = '#fec502';

        newCloud = createOrderCloud(messageData);
    }
    else if (messageData.message_type ==='document'){
        let fileDocumentPath = messageData.text;
        let targetDocument = "messageCloud" + messageData.message_id;
        messageData.text = 'document';
        newCloud = createTextCloud(messageData);
        newCloud.classList.add('historyDocument');
        const textContainer = newCloud.querySelector('.oneMessageText')
        const cloneTimeElement = textContainer.querySelector('.timeElement').cloneNode(true);
        textContainer.textContent = null;
        const buttonDiv = document.createElement('div');
        buttonDiv.path = messageData.file_path,
        buttonDiv.targetID = newCloud.id;
        buttonDiv.classList.add('documentButton');
        buttonDiv.textContent = 'Document';
        buttonDiv.addEventListener("click", function() {
            sendAskForFile(targetDocument, fileDocumentPath,ws);
        });
        textContainer.appendChild(buttonDiv);
        textContainer.appendChild(cloneTimeElement);
    }
    else if (messageData.message_type ==='photo'){
                file_path = messageData.text;
                messageData.text ='photo';
                newCloud = createTextCloud(messageData);
                newCloud.filePath = file_path;
                newCloud.classList.add('historyPhoto');
                }

    else if (messageData.message_type ==='fastPhoto'){
                let file_path = messageData.text;
                let target = "messageCloud"+messageData.message_id;
                messageData.text ='photo';
                newCloud = createTextCloud(messageData);
                newCloud.filePath = file_path;
                newCloud.classList.add('historyPhoto');
                sendAskForFile(target,file_path,ws);
    }
    else {
    console.error('Unknown message_type')
    return;
    }

    newCloud.classList.add(spacer_report.separateClass);

    if (spacer_report.details !== null) {
        anotherCloud = createManagerCloud(spacer_report.details);
        messageWindow.appendChild(anotherCloud);
    }
    messageWindow.appendChild(newCloud);
    return newCloud;
}

const initWssConnection = (token, url) => {
    const ws = new WebSocket(url);
    ws.onopen = function () {
        let data = {
            event: "onconnect",
            token: token,
        };
        ws.send(JSON.stringify(data));
        let message = document.getElementById('messageWindow');
        message.scrollTop = message.scrollHeight;

        const simafor = document.getElementById('simaFor');
        simafor.classList.add("simaGreen");
    };
    ws.onmessage = function (event) {
        const incomeData = JSON.parse(event.data);
        console.log(incomeData);
        let messageEvent;
        messageEvent = incomeData.event;
        const messageWind = document.getElementById('messageWindow');
        switch (messageEvent) {
            case 'message':
                let newCloud = appendMessageCloud(incomeData.details,ws);
                messageWind.scrollTop = messageWind.scrollHeight;
                if (newCloud) {
                    observerIsRead.observe(newCloud)
                }
                break;
            case 'authorization':
                if (incomeData.result === 'success') {
                    let data = {'event':'download_history'};
                    ws.send(JSON.stringify(data));
                } else {
                    console.warn(`UNSUCCESSFUL ${incomeData}`);
                }
                break;

            case 'download_history':
                let messages = incomeData.data;
                console.log(messages);

                for (let i = 0; i < messages.length; i++) {
                    appendMessageCloud(messages[i],ws);
                }
                messageWind.scrollTop = messageWind.scrollHeight;

                const photoBlocks = document.querySelectorAll('.historyPhoto');
                photoBlocks.forEach(block => {
                    observerPhoto.observe(block);
                });
                const messagesReadOrUnread = document.querySelectorAll('.oneMessageContainer');
                messagesReadOrUnread.forEach(block => {
                    const blockId = block.id;
                    if (blockId) {
                        observerIsRead.observe(block);
                    }
                })
                break;
            case 'fileDownload':
                let document_or_photo = incomeData.details.document_or_photo;
                if (document_or_photo === "photo"){
                    const downloadedPhoto = createImageFromBase64(incomeData.details.file,incomeData.details.mimi_type);
                    downloadedPhoto.addEventListener('click', toggleFullScreenImage);
                    const targetContainer = document.getElementById(incomeData.details.targetID).querySelector('.oneMessageText');
                    const timeElement = targetContainer.querySelector('.timeElement');
                    const cloneTimeElement = timeElement.cloneNode(true);
                    targetContainer.textContent = null;
                    const clonedElement = targetContainer.cloneNode(true);
                    targetContainer.replaceWith(clonedElement);
                    clonedElement.prepend(downloadedPhoto);
                    clonedElement.appendChild(cloneTimeElement);

                } else if (document_or_photo === "document") {

                const fileDocument = base64ToFile(incomeData.details.file,incomeData.details.mimi_type);
                downloadFile(fileDocument, document);
                }
                break;
            case 'openAddButton':
                let buttonAddFileSecret = document.getElementById('buttonAddFile');
                buttonAddFileSecret.classList.remove('buttonAddFileContainerInactive');
                buttonAddFileSecret.classList.add('buttonAddFileContainer');
                buttonAddFileSecret.disabled = false;
                break;
        }
    };

    ws.onclose = function (event) {
        const newCloud = createErrorCloud();
        const messageWindow = document.getElementById('messageWindow');
        const simafor = document.getElementById('simaFor');
        simafor.classList.remove("simaGreen");
        simafor.classList.add("simaRed");


        if (event.wasClean) {
            console.log(`Соединение закрыто чисто, код=${event.code}, причина=${event.reason}`);
            messageWindow.appendChild(newCloud);
        } else {
            console.warn('Соединение разорвано со стороны сервера');
            messageWindow.appendChild(newCloud);
        }
        messageWindow.scrollTop = messageWindow.scrollHeight;
    };
    ws.onerror = function (error) {
        console.error('Произошла ошибка:', error);
        const newCloud = createErrorCloud();
        const messageWindow = document.getElementById('messageWindow');
        messageWindow.appendChild(newCloud);
        messageWindow.scrollTop = messageWindow.scrollHeight;
        const simafor = document.getElementById('simaFor');
        simafor.classList.remove("simaGreen");
        simafor.classList.add("simaRed");
    };
return ws;
}

function toggleFullScreenImage(event) {
    const img = event.target;
    if (!img.classList.contains('fullscreen-image')) {
        img.classList.add('fullscreen-image');
        img.style.position = 'fixed';
        img.style.top = '0';
        img.style.left = '0';
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'contain';
        img.style.zIndex = '9999';
        img.style.backgroundColor = 'white';
        img.style.transition = 'ease-in-out 0.3s';
    } else {
        img.classList.remove('fullscreen-image');
        img.style.position = '';
        img.style.top = '';
        img.style.left = '';
        img.style.width = '';
        img.style.height = '';
        img.style.objectFit = '';
        img.style.zIndex = '';
        img.style.backgroundColor = '';
    }
}

const accessToken = exportToken;
const socketUrl =   "wss://supportstation.kz/ws/";

console.log('accessToken', accessToken);
const ws = initWssConnection(accessToken, socketUrl);
console.log("ADD LISTENER TO CONSTRACTION...............1 inputText");
document.getElementById('inputText').addEventListener('input', function () {
    let textareaValue = this.value.trim();
    let clearButton = document.getElementById('buttonSendText');
    if (textareaValue !== '') {
        clearButton.classList.remove('buttonSendContainerInactive');
        clearButton.classList.add('buttonSendContainerActive');
        clearButton.disabled = false;
    } else {
        clearButton.classList.remove('buttonSendContainerActive');
        clearButton.classList.add('buttonSendContainerInactive');
        clearButton.disabled = true;
    }
});

console.log("ADD LISTENER TO CONSTRACTION............... 2 buttonSendText");
let buttonSendMessage = document.getElementById("buttonSendText");
buttonSendMessage.addEventListener('click', function () {
    let textarea = document.getElementById("inputText");
    let messageLoad = {
        'event': 'message',
        'name': new_user,
        'details': {
            'is_answer': false,
            'message_type': 'text',
            'text': textarea.value,
            'message_id': null,
            'user_id': null,
        }
    };
    textarea.value = '';
    textarea.style.height = 'auto';
    let sendBuTTON = document.getElementById('buttonSendText');
    sendBuTTON.classList.remove('buttonSendContainerActive');
    sendBuTTON.classList.add('buttonSendContainerInactive');
    sendBuTTON.disabled = true;
    ws.send(JSON.stringify(messageLoad));
});
        console.log("ADD LISTENER TO CONSTRACTION............... 3 ");

        const buttonAddFileSecret = document.getElementById('buttonAddFile');
        buttonAddFileSecret.addEventListener('click',uploadFile);

        function uploadFile() {
           console.log("START foo UPLOAD FILE");
           const fileInput = document.getElementById('fileInput');
           fileInput.click();
        }
        console.log("ADD LISTENER TO CONSTRACTION............... 4 ");
        const inputAddFile = document.getElementById('fileInput');
        inputAddFile.addEventListener('change',function() {
        const file = event.target.files[0];
        if (file) {
            buttonAddFileSecret.classList.remove('buttonAddFileContainer');
            buttonAddFileSecret.classList.add('buttonAddFileContainerInactive');
            buttonAddFileSecret.disabled = true;
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = function(event) {
                const base64String = event.target.result.split(',')[1];
                const data = {
                        'event': 'uploadStatic',
                        'name': new_user,
                        'details': {
                            'message_id': null,
                            'is_answer': false,
                            'file_name': file.name,
                            'file_string': base64String
                        }
                    };
                const fileSize = file.size;
                const maxSize = 15 * 1024 * 1024;
                if (fileSize > maxSize) {
                    alert('Файл слишком большой. Максимальный размер файла: 15 МБ.');
                    } else {
                ws.send(JSON.stringify(data));
                }
            }
        }else {
        console.log('Файл не выбран.');
        }
        });
    })







export const initWssConnection = (token, url) => {
        console.log('start init wss connection');
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
            }, options)
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
            console.log(incomeData);
            let messageEvent;
            messageEvent = incomeData.event;
            const messageWind = document.getElementById('messageWindow');
            switch (messageEvent) {
                case 'message':
                    let NewCloudAppended = appendMessageCloud(incomeData.details, ws);
                    messageWind.scrollTop = messageWind.scrollHeight;
                    if (NewCloudAppended.id) {
                        console.log('pew pew observer')
                        observerIsRead.observe(NewCloudAppended);
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
            if (event.wasClean) {
                console.log(`Соединение закрыто чисто, код=${event.code}, причина=${event.reason}`);
            } else {
                console.warn('Соединение разорвано со стороны сервера');
            }
            const newCloud = createErrorCloud();
            const messageWindow = document.getElementById('messageWindow');
            messageWindow.appendChild(newCloud);
            messageWindow.scrollTop = messageWindow.scrollHeight;
            const simafor = document.getElementById('simaFor');
            simafor.classList.remove("simaGreen");
            simafor.classList.add("simaRed");
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
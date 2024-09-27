
export const initWssConnectionUnread = (token, url) => {
    console.log('starting ws2');
    const ws2 = new WebSocket(url);
    ws2.onopen = function () {
        let data = {
            event: "onconnect",
            token: token,
        };
        ws2.send(JSON.stringify(data));
    };
    ws2.onmessage = function (event) {
        console.log('message incoming wss2')
        const incomeData = JSON.parse(event.data);
        console.log(incomeData);
        let messageEvent;
        messageEvent = incomeData.event;
        switch (messageEvent) {
            case "authorization":
                console.log('send ask for count Authorization success');
                let data2 = {event: 'getUnreadMessageCount'};
                console.log(data2);
                ws2.send(JSON.stringify(data2));
                break;
            case 'UnreadMessageCount':
                console.log('UnreadMessageCount event START!');
                if (incomeData.details.count === 0) {
                    return ws2;
                }
                console.log('start MAGIC!!!!!!!!!!!!!!!!');
                let messageButton = document.getElementById('messengerMiniButton');
                let messageButton2 = document.getElementById('messengerMiniButton2');
                let messagesCounter = updateSquareCounter(incomeData.details.count);
                let messagesCounter2 = updateSquareCounter2(incomeData.details.count);

                if (incomeData.details.count > 0) {
                    messageButton.classList.add('createSignal');
                    messagesCounter.classList.add('createSignal');

                    messageButton2.classList.add('createSignal');
                    messagesCounter2.classList.add('createSignal');
                } else {
                    messageButton.classList.remove('createSignal');
                    messagesCounter.classList.remove('createSignal');

                    messageButton2.classList.remove('createSignal');
                    messagesCounter2.classList.remove('createSignal');
                }
                break;
        }
    }
    ws2.onclose = function (event) {
        console.log('[Закрылося WSS 2]');
    };
    ws2.onerror = function (error) {
        console.error('[Произошла ошибка WSS 2:]', error);
    };
    return ws2;
}
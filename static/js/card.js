$.noConflict();
jQuery(function ($) {
    
    function getCardType(number) {
        const numberFormated = number.replace(/\D/g, '')
        var patterns = {
            VISA: /^4[0-9]{12}(?:[0-9]{3})?$/,
            MASTER: /^5[1-5][0-9]{14}$/,
            AMEX: /^3[47][0-9]{13}$/,
            ELO: /^((((636368)|(438935)|(504175)|(451416)|(636297))\d{0,10})|((5067)|(4576)|(4011))\d{0,12})$/,
            AURA: /^(5078\d{2})(\d{2})(\d{11})$/,
            JCB: /^(?:2131|1800|35\d{3})\d{11}$/,
            DINERS: /^3(?:0[0-5]|[68][0-9])[0-9]{11}$/,
            DISCOVERY: /^6(?:011|5[0-9]{2})[0-9]{12}$/,
            HIPERCARD: /^(606282\d{10}(\d{3})?)|(3841\d{15})$/,
            ELECTRON: /^(4026|417500|4405|4508|4844|4913|4917)\d+$/,
            MAESTRO: /^(5018|5020|5038|5612|5893|6304|6759|6761|6762|6763|0604|6390)\d+$/,
            DANKORT: /^(5019)\d+$/,
            INTERPAYMENT: /^(636)\d+$/,
            UNIONPAY: /^(62|88)\d+$/,
        }
        for (var key in patterns) {
            if (patterns[key].test(numberFormated)) {
                return key
            }
        }
    }

});
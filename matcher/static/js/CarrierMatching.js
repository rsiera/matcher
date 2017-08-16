(function ($) {
    // Models
    function Carrier(name, city, id) {
        this.name = name;
        this.city = city;
        this.id = id;
    }

    Carrier.prototype.firstPartOfName = function () {
        return this.name.split(' ')[0];
    };

    function CarrierMatcher(pool) {
        this.pool = pool;
        this.matchUrl = pool.matchUrl;
    }

    CarrierMatcher.prototype.match = function (carrierRow) {
        carrierRow.matchingStarted();

        var carrier = carrierRow.carrier;
        var data = {
            'city': carrier.city,
            'name': carrier.firstPartOfName()
        };

        var jqXHR = $.getJSON(this.matchUrl, data);

        jqXHR.done(function (data) {
            carrierRow.matched(data);
        });

        jqXHR.fail(function (jqXHR, status) {
            console.log(carrierRow.rowNumber, carrier.name, status);
            carrierRow.matchFailed();
        });

        jqXHR.always($.proxy(this.returnToPool, this))
    };

    CarrierMatcher.prototype.returnToPool = function () {
        this.pool.notify(this);
    };

    function CarrierMatcherPool(matchUrl, size) {
        this.matchUrl = matchUrl;
        this.matchers = this.makeMatchers(size);
        this.free = this.matchers.slice();
        this.queue = [];
    }

    CarrierMatcherPool.prototype.makeMatchers = function (size) {
        var i, matchers = [];
        for (i = 0; i < size; i++) {
            matchers.push(new CarrierMatcher(this));
        }
        return matchers;
    };

    CarrierMatcherPool.prototype.match = function (carrierRow) {
        if (this.free.length > 0) {
            var matcher = this.free.pop();
            matcher.match(carrierRow);
        } else {
            this.queue.push(carrierRow);
        }
    };

    CarrierMatcherPool.prototype.notify = function (matcher) {
        if (this.queue.length > 0) {
            var carrierRow = this.queue.shift();
            matcher.match(carrierRow);
        } else {
            this.free.push(matcher);
        }
    };


    // Views
    function CarrierRow(elem, table) {
        this.table = table;
        this.done = false;
        this.elem = $(elem);
        this.rowNumber = this.elem.find('.row-number').text();
        var matchesElem = this.elem.find('.carrier-matches');
        this.matchesCell = new MatchesCell(matchesElem, this.rowNumber);
        this.carrier = this.makeCarrier();
    }

    CarrierRow.prototype.makeCarrier = function () {
        var name = this.elem.find('.carrier-name').text();
        var city = this.elem.find('.carrier-city').text();
        var id = this.elem.find('.carrier-id').val();
        return new Carrier(name, city, id);
    };

    CarrierRow.prototype.setDone = function () {
        this.done = true;
        this.table.matchDone();
    };

    CarrierRow.prototype.matched = function (data) {
        var matches = data['matches'];
        this.matchesCell.setData(matches);
        this.setDone();
    };

    CarrierRow.prototype.matchFailed = function () {
        this.matchesCell.matchFailed();
        this.setDone();
    };

    CarrierRow.prototype.matchingStarted = function () {
        this.matchesCell.matchingStarted();
    };

    CarrierRow.prototype.update = function () {
        var checkedInputs = this.matchesCell.elem.find('input:checked');
        var carrierId = checkedInputs.first().val();
        var agreementId = $(checkedInputs[1]).val();

        this.carrier.id = carrierId;
        this.elem.find('.carrier-id').val(carrierId);
        this.elem.find('.agreement-id').val(agreementId);
    };

    function MatchesCell(elem, rowNumber) {
        this.elem = $(elem);
        this.rowNumber = rowNumber;
    }

    function markInitialRadio(radios, empty) {
        if (radios.length == 0) {
            empty.find('input').attr('checked', 'checked');
        } else if (radios.length == 1) {
            var companyRadio = radios[0].find('input').first();
            companyRadio.attr('checked', 'checked');
            var agreementRadios = radios[0].find('ul input');
            if (agreementRadios.length == 2) {
                var nonEmptyRadio = agreementRadios.filter('[value!=""]')[0];
                nonEmptyRadio.checked = true;
            }
            var agreementsForCompany = radios[0].closest('li').find('ul');
            agreementsForCompany.show();
        }
    }

    function setInitialAgreementRadios(agreementsForCompany) {
        agreementsForCompany.show();
        var availableRadios = agreementsForCompany.find('li input');

        if (availableRadios.length == 1) {
            availableRadios[0].checked = true;
        }
        else if (availableRadios.length == 2) {
            var nonEmptyRadio = availableRadios.filter('[value!=""]')[0];
            nonEmptyRadio.checked = true;
        }
    }

    function hideOpenedAgreementRadios() {
        $(this).parents('ul').find('li ul').each(function () {
            $(this).hide();
        });
    }

    function uncheckAgreementRadios() {
        $(this).closest('ul').find('ul li input').each(function () {
            this.checked = false;
        });
    }

    MatchesCell.prototype.setData = function (matches) {
        var noMatchCompany = this.makeRadio({'name': 'No match'});
        noMatchCompany.find('input').change(function () {
            hideOpenedAgreementRadios.call(this);
            uncheckAgreementRadios.call(this);
        });

        var companyRadios = [];

        for (var i = 0; i < matches.length; i++) {
            var match = matches[i];
            var companyRadio = this.makeRadio(match);

            companyRadio.find('input').change(function () {
                hideOpenedAgreementRadios.call(this);
                uncheckAgreementRadios.call(this);

                if ($(this).is(":checked")) {
                    var agreementRadios = $(this).closest('li').find('ul');
                    setInitialAgreementRadios(agreementRadios);
                }
            });

            if (match['agreements'].length > 0) {
                var agreementsList = this.makeAgreementsForCompany(match);
                companyRadio.append(agreementsList);
            }
            companyRadios.push(companyRadio);
        }

        markInitialRadio(companyRadios, noMatchCompany);
        var ul = $('<ul>');
        ul.append(noMatchCompany);
        ul.append(companyRadios);
        this.elem.empty().append(ul);
    };

    MatchesCell.prototype.makeAgreementsForCompany = function (match) {
        var agreementRadios = $.map(match['agreements'], $.proxy(this.makeRadio, this));
        var noMatchAgreement = this.makeRadio({'name': 'No match', 'Id': match['id']});
        var ul = $('<ul>');
        ul.append(noMatchAgreement);
        ul.append(agreementRadios);
        ul.hide();
        return ul;
    };

    MatchesCell.prototype.matchFailed = function () {
        this.elem.empty().text('Error matching company');
    };

    MatchesCell.prototype.matchingStarted = function () {
        this.elem.empty().text('In progress...');
    };

    MatchesCell.prototype.makeRadio = function (match) {
        var text = match['name'], value = match['id'];
        var url = match['url'];
        var Id = match['Id'] || '';

        var radio = $('<input>').attr({
            'type': 'radio',
            'name': 'match-' + this.rowNumber + Id,
            'value': value || ""
        });

        if (url) {
            text = $('<a>').attr('href', url).text(text);
            text.on('click', function () {
                window.open(this.href);
                return false
            });
        }

        var label = $('<label>').append(radio).append(text);
        return  $('<li>').append(label);
    };

    function CarrierTable(elem) {
        this.matchedRows = 0;
        this.elem = $(elem);
        this.matchUrl = this.elem.data('match-url');
        this.carrierRows = this.makeCarrierRows();

        this.elem.closest('form').on('submit', $.proxy(this.onSubmit, this));
    }

    CarrierTable.prototype.makeCarrierRows = function () {
        var carrierRows = [];
        var tableRows = this.elem.find('.carrier-row');
        var that = this;
        tableRows.each(function (index, rowElem) {
            carrierRows.push(new CarrierRow(rowElem, that));
        });
        return carrierRows;
    };

    CarrierTable.prototype.matchCarriers = function () {
        var matchUrl = this.matchUrl;
        var pool = new CarrierMatcherPool(matchUrl, 4);

        $.each(this.carrierRows, function (index, carrierRow) {
            pool.match(carrierRow);
        });
    };

    CarrierTable.prototype.onSubmit = function () {
        $.each(this.carrierRows, function (index, carrierRow) {
            carrierRow.update();
        });
    };

    CarrierTable.prototype.matchDone = function () {
        this.matchedRows += 1;

        if (this.matchedRows === this.carrierRows.length) {
            this.elem.find('button').attr('disabled', null);
        }
    };


    // MAIN
    var main = function () {
        var carrierTable = new CarrierTable('#carrier-table');
        carrierTable.matchCarriers();

        window.carrierTable = carrierTable;
    };

    // Run on document load
    $(main);

// use newer jQuery
})(django.jQuery);

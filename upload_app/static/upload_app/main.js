$(() => {
  function checkInputs() {
    const fields = [
      '#id_trans_num',
      '#id_ccd_num',
      '#id_port_of_entry',
      '#id_eta_date',
      '#id_eta_time',
    ];

    for (let i = 0; i < fields.length; i += 1) {
      if ($(fields[i]).val() !== '') {
        return true;
      }
    }
    return false;
  }
  /*
  If filename contains a date in the format YYYYMMDD the eta_date field will be
  filled with the date.
  
  If it is followed by a time in the format HHMM the eta_time field will be
  filled with the time.
  */
  function dateTimeFromFilename(filename) {
    const dateReString = '20\\d{2}([-._]{0,1})[0-1]\\d\\1[0-3]\\d';
    const dateRe = new RegExp(dateReString);
    let etaDate = filename.match(dateRe);
    if (etaDate) {
      etaDate = etaDate[0].replace(/[-._]/g, '');
      etaDate = [
        etaDate.slice(0, 4),
        etaDate.slice(4, 6),
        etaDate.slice(6),
      ];
      $('#id_eta_date').val(etaDate.join('-'));
    }
    const timeRe = new RegExp(`${dateReString}[-._]{0,1}[0-2]\\d{3}`);
    let etaTime = filename.match(timeRe);
    if (etaTime) {
      etaTime = etaTime[0].replace(/[-._]/g, '').slice(-4);
      etaTime = [etaTime.slice(0, 2), etaTime.slice(2)];
      $('#id_eta_time').val(etaTime.join(':'));
    }
  }

  function definedFormatParser(filename) {
    const filenameArray = filename.split('_');
    $('#id_port_of_entry').val(filenameArray[1]);
    $('#id_ccd_num').val(filenameArray[2]);
    $('#id_trans_num').val(filenameArray[3]);
    const etaDate = [
      filenameArray[5].slice(0, 4),
      filenameArray[5].slice(4, 6),
      filenameArray[5].slice(6),
    ];
    $('#id_eta_date').val(etaDate.join('-'));
    const etaTime = [
      filenameArray[6].slice(0, 2),
      filenameArray[6].slice(2),
    ];
    $('#id_eta_time').val(etaTime.join(':'));
  }

  function displayFilename(filename) {
    if (filename.length > 20) {
      $('#filename-msg').text(
        `${filename.slice(0, 10)}...${filename.slice(-10)}`,
      );
    } else {
      $('#filename-msg').text(filename);
    }
  }

  function flipDisplay() {
    $('#msg').text('');
    const nowHidden = $('.hide');
    const nowShowing = $('.show');
    nowHidden.removeClass('hide').addClass('show');
    nowShowing.removeClass('show').addClass('hide');
  }

  function getCsrf() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i += 1) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === 'csrftoken=') {
          cookieValue = decodeURIComponent(cookie.substring(10));
          break;
        }
      }
    }
    return cookieValue;
  }

  function numbersFromFilename(filename) {
    const filenameArray = filename.split(/[-\s_.]/);
    filenameArray.forEach((filenameSegment) => {
      const segmentAsNum = parseInt(filenameSegment, 10);
      if (!Number.isNaN(segmentAsNum)) {
        switch (filenameSegment.length) {
          case 14:
            $('#id_trans_num').val(filenameSegment);
            break;
          case 3:
            $('#id_port_of_entry').val(filenameSegment);
            break;
          default:
            break;
        }
      }
    });
  }

  function parseFilename(filename) {
    if (
      /\d{5}_\d{3}_[a-zA-Z0-9]{5,}_\d{14}_\d{6}_\d{8}_\d{4}.*/.test(
        filename,
      )
    ) {
      definedFormatParser(filename);
    } else {
      dateTimeFromFilename(filename);
      numbersFromFilename(filename);
    }
  }

  function resetPage() {
    $('form')[0].reset();
    $('.msg').text('');
    flipDisplay();
  }

  $(document).on('dragover drop dragenter', (e) => {
    e.preventDefault();
  });

  $('#dropbox').on('dragover dragenter', () => {
    $('#dropbox').addClass('dropbox-hover');
  });

  $('#dropbox').on('drop dragleave', () => {
    $('#dropbox').removeClass('dropbox-hover');
  });

  $('#dropbox').on('drop', (e) => {
    const file = e.originalEvent.dataTransfer.files;

    if (file.length > 1) {
      $('#msg').text('Please upload only one file at a time.');
    } else {
      const filename = file[0].name;
      $('#id_userfile').prop('files', file);
      displayFilename(filename);
      flipDisplay();
      parseFilename(filename);
    }
    if (checkInputs()) {
      $('#msg').text(
        'Fields have been filled based on the filename, please check that they are all correct.',
      );
    }
  });

  $('#form-fields').on('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    $('.msg').text('');

    $.ajax({
      url: e.target.action,
      headers: { 'X-CSRFToken': getCsrf() },
      mode: 'same-origin',
      type: 'POST',
      data: formData,
      contentType: false,
      processData: false,
      success: (response) => {
        if (response.errors) {
          $.each(response.errors, (field, error) => {
            const concatenatedErrors = error.reduce(
              (acc, currentError) => acc + currentError.message,
              '',
            );
            $(`#${field} p.msg`).text(concatenatedErrors);
            $("input[name='submit-btn']").blur();
          });
        } else {
          resetPage();
          $('#msg').text(response);
        }
      },
    });
  });

  $('#go-back').on('click', () => {
    resetPage();
  });
});

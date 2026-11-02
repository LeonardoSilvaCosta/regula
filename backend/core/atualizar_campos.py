"""Recalcula PAGE e PAGEREF no Word, para o sumário e as listas terem a página real."""
import os


def atualizar_campos_word(caminho):
    """
    Abre o .docx no Microsoft Word, atualiza todos os campos e salva.
    Sem isso, PAGEREF fica em 0 até o usuário atualizar manualmente.
    """
    caminho = os.path.abspath(caminho)
    if not os.path.isfile(caminho):
        print(f"[ADVERTENCIA] Arquivo não encontrado para atualizar campos: {caminho}")
        return False

    word = None
    doc = None
    try:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(caminho, ReadOnly=False, AddToRecentFiles=False)
        doc.Fields.Update()
        for secao in doc.Sections:
            for idx in (1, 2, 3):
                secao.Headers(idx).Range.Fields.Update()
                secao.Footers(idx).Range.Fields.Update()
        doc.Repaginate()
        doc.Fields.Update()
        wd_portugues_brasil = 1046
        doc.Content.LanguageID = wd_portugues_brasil
        for secao in doc.Sections:
            for idx in (1, 2, 3):
                secao.Headers(idx).Range.LanguageID = wd_portugues_brasil
                secao.Footers(idx).Range.LanguageID = wd_portugues_brasil
        doc.Save()
        print("[OK] Páginas do sumário e das listas recalculadas pelo Word.")
        return True
    except ImportError:
        print(
            "[ADVERTENCIA] pywin32 não está instalado. "
            "As páginas do sumário só serão atualizadas ao abrir o arquivo no Word."
        )
        return False
    except Exception as erro:
        print(
            f"[ADVERTENCIA] Não foi possível recalcular as páginas automaticamente: {erro}. "
            "Abra o documento no Word e pressione Ctrl+A e F9."
        )
        return False
    finally:
        try:
            if doc is not None:
                doc.Close(SaveChanges=True)
        except Exception:
            pass
        try:
            if word is not None:
                word.Quit()
        except Exception:
            pass
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except Exception:
            pass

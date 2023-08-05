/*
    Copyright (C) 2008 Nokia Corporation and/or its subsidiary(-ies)
    Copyright (C) 2007 Staikos Computing Services Inc.

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public License
    along with this library; see the file COPYING.LIB.  If not, write to
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
    Boston, MA 02110-1301, USA.
*/

#ifndef QWEBVIEW_H
#define QWEBVIEW_H

#include <QtWebKit/qwebkitglobal.h>
#include <QtWebKitWidgets/qwebpage.h>
#include <QtCore/qurl.h>
#include <QtGui/qicon.h>
#include <QtGui/qpainter.h>
#include <QtNetwork/qnetworkaccessmanager.h>
#include <QtWidgets/qwidget.h>

QT_BEGIN_NAMESPACE
class QNetworkRequest;
class QPrinter;
QT_END_NAMESPACE

class QWebPage;
class QWebViewPrivate;
class QWebNetworkRequest;

class QWEBKITWIDGETS_EXPORT QWebView : public QWidget {
    Q_OBJECT
    Q_PROPERTY(QString title READ title)
    Q_PROPERTY(QUrl url READ url WRITE setUrl)
    Q_PROPERTY(QIcon icon READ icon)
    Q_PROPERTY(QString selectedText READ selectedText)
    Q_PROPERTY(QString selectedHtml READ selectedHtml)
    Q_PROPERTY(bool hasSelection READ hasSelection)
    Q_PROPERTY(bool modified READ isModified)
    //Q_PROPERTY(Qt::TextInteractionFlags textInteractionFlags READ textInteractionFlags WRITE setTextInteractionFlags)
    Q_PROPERTY(qreal textSizeMultiplier READ textSizeMultiplier WRITE setTextSizeMultiplier DESIGNABLE false)
    Q_PROPERTY(qreal zoomFactor READ zoomFactor WRITE setZoomFactor)

    Q_PROPERTY(QPainter::RenderHints renderHints READ renderHints WRITE setRenderHints)
    Q_FLAGS(QPainter::RenderHints)
public:
    explicit QWebView(QWidget* parent = Q_NULLPTR);
    ~QWebView();

    QWebPage* page() const;
    void setPage(QWebPage* page);

    void load(const QUrl& url);
    void load(const QNetworkRequest& request, QNetworkAccessManager::Operation operation = QNetworkAccessManager::GetOperation, const QByteArray &body = QByteArray());
    void setHtml(const QString& html, const QUrl& baseUrl = QUrl());
    void setContent(const QByteArray& data, const QString& mimeType = QString(), const QUrl& baseUrl = QUrl());

    QWebHistory* history() const;
    QWebSettings* settings() const;

    QString title() const;
    void setUrl(const QUrl &url);
    QUrl url() const;
    QIcon icon() const;

    bool hasSelection() const;
    QString selectedText() const;
    QString selectedHtml() const;

#ifndef QT_NO_ACTION
    QAction* pageAction(QWebPage::WebAction action) const;
#endif
    void triggerPageAction(QWebPage::WebAction action, bool checked = false);

    bool isModified() const;

    /*
    Qt::TextInteractionFlags textInteractionFlags() const;
    void setTextInteractionFlags(Qt::TextInteractionFlags flags);
    void setTextInteractionFlag(Qt::TextInteractionFlag flag);
    */

    QVariant inputMethodQuery(Qt::InputMethodQuery property) const Q_DECL_OVERRIDE;

    QSize sizeHint() const Q_DECL_OVERRIDE;

    qreal zoomFactor() const;
    void setZoomFactor(qreal factor);

    void setTextSizeMultiplier(qreal factor);
    qreal textSizeMultiplier() const;

    QPainter::RenderHints renderHints() const;
    void setRenderHints(QPainter::RenderHints hints);
    void setRenderHint(QPainter::RenderHint hint, bool enabled = true);

    bool findText(const QString& subString, QWebPage::FindFlags options = QWebPage::FindFlags());

    bool event(QEvent*) Q_DECL_OVERRIDE;

public Q_SLOTS:
    void stop();
    void back();
    void forward();
    void reload();

    void print(QPrinter*) const;

Q_SIGNALS:
    void loadStarted();
    void loadProgress(int progress);
    void loadFinished(bool);
    void titleChanged(const QString& title);
    void statusBarMessage(const QString& text);
    void linkClicked(const QUrl&);
    void selectionChanged();
    void iconChanged();
    void urlChanged(const QUrl&);

protected:
    void resizeEvent(QResizeEvent*) Q_DECL_OVERRIDE;
    void paintEvent(QPaintEvent*) Q_DECL_OVERRIDE;

    virtual QWebView *createWindow(QWebPage::WebWindowType type);

    void changeEvent(QEvent*) Q_DECL_OVERRIDE;
    void mouseMoveEvent(QMouseEvent*) Q_DECL_OVERRIDE;
    void mousePressEvent(QMouseEvent*) Q_DECL_OVERRIDE;
    void mouseDoubleClickEvent(QMouseEvent*) Q_DECL_OVERRIDE;
    void mouseReleaseEvent(QMouseEvent*) Q_DECL_OVERRIDE;
#ifndef QT_NO_CONTEXTMENU
    void contextMenuEvent(QContextMenuEvent*) Q_DECL_OVERRIDE;
#endif
#ifndef QT_NO_WHEELEVENT
    void wheelEvent(QWheelEvent*) Q_DECL_OVERRIDE;
#endif
    void keyPressEvent(QKeyEvent*) Q_DECL_OVERRIDE;
    void keyReleaseEvent(QKeyEvent*) Q_DECL_OVERRIDE;
    void dragEnterEvent(QDragEnterEvent*) Q_DECL_OVERRIDE;
    void dragLeaveEvent(QDragLeaveEvent*) Q_DECL_OVERRIDE;
    void dragMoveEvent(QDragMoveEvent*) Q_DECL_OVERRIDE;
    void dropEvent(QDropEvent*) Q_DECL_OVERRIDE;
    void focusInEvent(QFocusEvent*) Q_DECL_OVERRIDE;
    void focusOutEvent(QFocusEvent*) Q_DECL_OVERRIDE;
    void inputMethodEvent(QInputMethodEvent*) Q_DECL_OVERRIDE;

    bool focusNextPrevChild(bool next) Q_DECL_OVERRIDE;

private:
    friend class QWebPage;
    QWebViewPrivate* d;
    Q_PRIVATE_SLOT(d, void _q_pageDestroyed())
};

#endif // QWEBVIEW_H

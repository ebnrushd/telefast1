import asyncio
import os
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import auth
import bot
from models import TemplateCreate, SendMessageRequest

# --- App Initialization ---
app = FastAPI(title="Telegram Marketing Bot API")
ptb_app = bot.create_application()

# --- Bot Lifecycle ---
@app.on_event("startup")
async def startup_event():
    await ptb_app.initialize()
    await ptb_app.start()

@app.on_event("shutdown")
async def shutdown_event():
    await ptb_app.stop()

# --- API Endpoints ---

# Authentication
@app.post("/api/login", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    api_user = os.getenv("API_USER")
    api_password = os.getenv("API_PASSWORD")
    # Simplified password check for this single-user admin panel
    if not (form_data.username == api_user and form_data.password == api_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Statistics
@app.get("/api/stats", tags=["Statistics"])
async def get_stats(current_user: dict = Depends(auth.get_current_user)):
    user_count = len(bot.get_user_ids())
    chat_count = len(bot.load_chats())
    return {"user_count": user_count, "chat_count": chat_count}

# Chats
@app.get("/api/chats", tags=["Chats"])
async def get_chats(current_user: dict = Depends(auth.get_current_user)):
    return bot.load_chats()

# Templates
@app.get("/api/templates", tags=["Templates"])
async def get_templates(current_user: dict = Depends(auth.get_current_user)):
    return bot.load_templates()

@app.post("/api/templates", tags=["Templates"])
async def create_template(template: TemplateCreate, current_user: dict = Depends(auth.get_current_user)):
    bot.save_template(template.name, template.content, template.button_text, str(template.button_url) if template.button_url else None)
    return {"status": "success", "template_name": template.name}

@app.delete("/api/templates/{template_name}", tags=["Templates"])
async def delete_template_api(template_name: str, current_user: dict = Depends(auth.get_current_user)):
    if bot.delete_template_from_file(template_name):
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Template not found")

# Messaging
@app.post("/api/send", tags=["Messaging"])
async def send_message_api(request: SendMessageRequest, current_user: dict = Depends(auth.get_current_user)):
    templates = bot.load_templates()
    template = templates.get(request.template_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    reply_markup = None
    if "button_text" in template and "button_url" in template:
        button = InlineKeyboardButton(template["button_text"], url=template["button_url"])
        reply_markup = InlineKeyboardMarkup([[button]])

    try:
        await ptb_app.bot.send_message(
            chat_id=request.chat_id,
            text=template['content'],
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return {"status": "success", "detail": f"Message sent to {request.chat_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

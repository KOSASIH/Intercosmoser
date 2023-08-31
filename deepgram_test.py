from deepgram import Deepgram
import asyncio
import aiohttp

# The API key you created in step 1
DEEPGRAM_API_KEY = '7d4195b8f992d78281eb45f063b767ea28aa4649'

# URL for the real-time streaming audio you would like to transcribe
URL = 'http://stream.live.vc.bbcmedia.co.uk/bbc_world_service'

async def main():

    # Initializes the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    # Create a websocket connection to Deepgram
    try:
        deepgramLive = await deepgram.transcription.live(
            { "smart_format": True, "model": "nova", "language": "en-US" }
        )
    except Exception as e:
        print(f'Could not open socket: {e}')
        return

    # Listen for the connection to close
    deepgramLive.registerHandler(deepgramLive.event.CLOSE, lambda _: print('Connection closed.'))

    # Listen for any transcripts received from Deepgram and write them to the console
    deepgramLive.registerHandler(deepgramLive.event.TRANSCRIPT_RECEIVED, print)

    # Listen for the connection to open and send streaming audio from the URL to Deepgram
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as audio:
            while True:
                data = await audio.content.readany()
                deepgramLive.send(data)

                # If no data is being sent from the live stream, then break out of the loop.
                if not data:
                    break

    # Indicate that we've finished sending data by sending the customary zero-byte message to the Deepgram streaming endpoint, and wait until we get back the final summary metadata object
    await deepgramLive.finish()

asyncio.run(main())

# If you're running this code in a Jupyter notebook, Jupyter is already running an event loop, so you'll need to replace the last line with:
#await main()
